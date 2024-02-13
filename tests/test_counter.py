"""
Test Cases for Counter Web Service

Create a service that can keep a track of multiple counters
- API must be RESTful - see the status.py file. Following these guidelines, you can make assumptions about
how to call the web service and assert what it should return.
- The endpoint should be called /counters
- When creating a counter, you must specify the name in the path.
- Duplicate names must return a conflict error code.
- The service must be able to update a counter by name.
- The service must be able to read the counter
"""
from unittest import TestCase

# we need to import the unit under test - counter
from src.counter import app 

# we need to import the file that contains the status codes
from src import status 

COUNTERS = {}

# We will use the app decorator and create a route called slash counters.
# specify the variable in route <name>
# let Flask know that the only methods that is allowed to called
# on this function is "POST".
@app.route('/counters/<name>', methods=['POST'])
def create_counter(name):
    """Create a counter"""
    app.logger.info(f"Request to create counter: {name}")
    global COUNTERS
    if name in COUNTERS:
        return {"Message":f"Counter {name} already exists"}, status.HTTP_409_CONFLICT
    COUNTERS[name] = 0
    return {name: COUNTERS[name]}, status.HTTP_201_CREATED

@app.route('/counters/<name>', methods=['PUT'])
def update_counter(name):
    """Update a counter"""
    global COUNTERS
    if name not in COUNTERS:
        # If the counter doesn't exist, return a 404 Not Found error
        return {"Message": f"Counter {name} does not exist"}, status.HTTP_404_NOT_FOUND

    # Increment the counter by 1
    COUNTERS[name] += 1

    # Return the updated counter value and a 200 OK status
    return {name: COUNTERS[name]}, status.HTTP_200_OK


@app.route('/counters/<name>', methods=['DELETE'])
def delete_counter(name):
    """Delete a counter"""
    global COUNTERS
    if name not in COUNTERS:
        return {"Message": f"Counter {name} does not exist"}, status.HTTP_404_NOT_FOUND
    del COUNTERS[name]
    return '', status.HTTP_204_NO_CONTENT

@app.route('/counters/<name>', methods=['GET'])
def read_counter(name):
    """Read a counter"""
    if name not in COUNTERS:
        return {"Message": f"Counter {name} does not exist"}, status.HTTP_404_NOT_FOUND
    return {name: COUNTERS[name]}, status.HTTP_200_OK


class CounterTest(TestCase):
    def setUp(self):
        self.client = app.test_client()



    """Counter tests"""
    def test_create_a_counter(self):
        """It should create a counter"""
        client = app.test_client()
        result = client.post('/counters/foo')
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_duplicate_a_counter(self):
        """It should return an error for duplicates"""
        result = self.client.post('/counters/bar')
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        result = self.client.post('/counters/bar')
        self.assertEqual(result.status_code, status.HTTP_409_CONFLICT)

    def test_update_a_counter(self):
        """It should update a counter"""
        # Create a new counter
        create_response = self.client.post('/counters/testcounter')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Get baseline counter value
        baseline_value = create_response.json['testcounter']
        
        # Update the counter
        update_response = self.client.put('/counters/testcounter')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # Check that the counter value has increased by 1
        updated_value = update_response.json['testcounter']
        self.assertEqual(updated_value, baseline_value + 1)


    def test_delete_a_counter(self):
        """It should delete a counter"""
        # Create a new counter
        create_response = self.client.post('/counters/testdelete')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Delete the counter
        delete_response = self.client.delete('/counters/testdelete')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the counter is deleted
        get_response = self.client.get('/counters/testdelete')
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

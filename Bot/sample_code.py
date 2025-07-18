def process_data(user_list, threshold):
    # This function takes a list of user dictionaries and an age threshold.
    # It should return a list of names for users older than the threshold.
    results = []
    for user in user_list:
        if user['age'] > threshold:
            results.append(user['name'])
    return results

def calculate_average(numbers):
    # A simple function to calculate the average of a list of numbers.
    if not numbers:
        return 0
    total = sum(numbers)
    return total / len(numbers)


from calculator import *
from testrail import APIClient

# Project ID from TestRail
PROJECT_ID = 37

# Status IDs
PASSED_ID = 1
FAILED_ID = 5
NEEDS_REVIEW = 6


def unit_test(case_details, unit):
    test_result = dict()
    test_result['case_id'] = case_details['case_id']

    unit_result = globals()[unit](case_details['input'])

    test_result['comment'] = build_comment(case_details['input'], case_details['expected_output'], unit_result)
    if str(unit_result) != case_details['expected_output']:
        test_result['status_id'] = FAILED_ID
    else:
        test_result['status_id'] = PASSED_ID

    return test_result


def build_comment(input_list, expected, received):
    return 'Input: ' + ','.join(input_list) + '\nexpected: ' \
        + str(expected) + '\nreceived: ' + str(received)


def parse_data(test_case_details):
    response = dict()
    response['case_id'] = test_case_details['id']
    response['input'] = test_case_details['custom_input_values'].split(',')
    response['expected_output'] = test_case_details['custom_expected_output']
    return response


def find_section_id(section_list, target_name):
    for section in section_list:
        if section['name'] == target_name:
            return section['id']
    return None


def run_tests(section_list, api):
    results_array = list()

    units_under_test = ['add', 'difference', 'product', 'abs_val', 'power']
    for unit in units_under_test:
        section_id = find_section_id(section_list, unit)
        test_cases = api.send_get('get_cases/' + str(PROJECT_ID) + '&section_id=' + str(section_id))
        for case in test_cases:
            parameters = parse_data(case)
            test_result = unit_test(parameters, unit)
            results_array.append(test_result)

    return results_array


def main():
    # Declare TestRail API
    testrail_api = APIClient(TESTRAIL_URL)
    testrail_api.user = TESTRAIL_EMAIL_ADDRESS
    testrail_api.password = TESTRAIL_API_TOKEN

    # Retrieve all sections for the project
    all_sections = testrail_api.send_get('get_sections/' + str(PROJECT_ID))

    # all_results will hold all test results and will be the body of the result submission to TestRail
    all_results = dict()
    all_results['results'] = list()
    all_results['results'] += run_tests(all_sections, testrail_api)

    # Create test run
    new_run = testrail_api.send_post('add_run/' + str(PROJECT_ID), {"name": "Webinar Math Tests",
                                                                    "include_all": True})
    # add results
    run_results = testrail_api.send_post('add_results_for_cases/' + str(new_run['id']), all_results)

    # Close test run
    testrail_api.send_post('close_run/' + str(new_run['id']), {})

    # Display some stuff
    # print(all_results)
    print('Testing Complete!\nResults available here: ' + TESTRAIL_URL + 'index.php?/runs/view/' + str(new_run['id']))
    pass


if __name__ == '__main__':
    main()

from creds import *
from testrail import APIClient
import sys
import datetime

client = APIClient(TESTRAIL_URL)
client.user = TESTRAIL_USER
client.password = TESTRAIL_API_TOKEN

RUN_ID = 371
project_id = 0
status_styles = {}


def make_report(test_run_id):
    indent = 1

    html_output = ''

    # Import structured header info
    with open('html_headers.html', 'r') as head_file:
        html_output += head_file.read()

    # Add body of html details
    html_output += get_run_info(test_run_id, indent + 1)

    # Add closing html elements
    html_output += close_element('div', indent)
    html_output += close_element('body', 0)
    html_output += close_element('html', 0)

    # Create html file
    with open('sample.html', 'w') as f:
        f.write(html_output)


def get_run_info(test_run_id, indent):
    try:
        request_uri = 'get_run/'
        request_uri += str(test_run_id)
        run_dict = client.send_get(request_uri)

        # Store project_id
        global project_id
        project_id = run_dict['project_id']

        run_html = ''
        run_html += add_indents(indent)
        run_html += '<h1>R' + str(run_dict['id']) + ': ' + run_dict['name'] + '</h1>\n'

        run_html += create_status_stats(run_dict, indent)

        run_html += create_sections(indent)

        return run_html

    except:
        e = sys.exc_info()[0]
        print('Error in get_run_info')
        print(vars(e))


def create_status_stats(run_details, indent):
    status_html = open_element('div', indent, 'gridContainer')

    indent += 1
    status_html += open_element('table', indent, 'grid')

    indent += 1
    status_html += open_element('colgroup', indent)

    status_html += add_full_element('col', indent + 1)
    status_html += add_full_element('col', indent + 1, None, 'info')
    status_html += close_element('colgroup', indent)
    status_html += open_element('tr', indent)

    status_html += add_full_element('td', indent + 1, 'Created On')
    time_string = datetime.datetime.utcfromtimestamp(run_details['created_on']).strftime("%m/%d/%Y")
    status_html += add_full_element('td', indent + 1, time_string, 'info')

    status_html += close_element('tr', indent)

    status_html += open_element('tr', indent)
    status_html += add_full_element('td', indent + 1, 'Completed')

    if run_details['completed_on']:
        status_html += add_full_element('td', indent + 1, 'Yes', 'info')
        status_html += close_element('tr', indent)
        status_html += open_element('tr', indent)
        status_html += add_full_element('td', indent + 1, 'Completed On')
        completed_date = datetime.datetime.utcfromtimestamp(run_details['completed_on']).strftime("%m/%d/%Y")
        status_html += add_full_element('td', indent + 1, completed_date, 'info')
        status_html += close_element('tr', indent)
    else:
        status_html += add_full_element('td', indent + 1, 'No', 'info')

    status_html += close_element('tr', indent)
    indent -= 1
    status_html += close_element('table', indent)

    status_html += close_element('div', indent - 1)
    status_html += open_element('div', indent - 1, 'gridContainer', 'margin-bottom: 1.5em')

    status_html += open_element('table', indent, 'grid')

    indent += 1
    status_html += open_element('colgroup', indent)

    for x in range(5):
        status_html += add_full_element('col', indent + 1, None, None, 'width: 20%')

    status_html += close_element('colgroup', indent)

    # Calculate total number of tests
    status_info = client.send_get('get_statuses')

    total_results = 0
    for status_entry in status_info:
        # Standard TestRail Status
        if status_entry['id'] < 6:
            status_string = status_entry['name']
            status_string += '_count'
        # Custom Status reported as custom_statusX_count
        else:
            status_string = 'custom_status' + str(status_entry['id'] - 5) + '_count'
        total_results += run_details[status_string]

        # Capture Status HTML Styling
        status_styles[status_entry['id']] = {}
        status_styles[status_entry['id']]['label'] = status_entry['label']
        status_styles[status_entry['id']]['bg_color'] = str(hex(status_entry['color_dark']))[2:]
        while len(status_styles[status_entry['id']]['bg_color']) < 6:
            status_styles[status_entry['id']]['bg_color'] = '0' + status_styles[status_entry['id']]['bg_color']

    # Build Table Rows for statuses
    header_row = open_element('tr', indent, 'header')
    data_row = open_element('tr', indent)

    indent += 1
    column_counter = 0
    for x in range(len(status_info)):
        if column_counter == 5:
            indent -= 1
            column_counter = 0
            header_row += close_element('tr', indent)
            data_row += close_element('tr', indent)
            status_html += header_row
            status_html += data_row
            header_row = open_element('tr', indent, 'header')
            data_row = open_element('tr', indent)
            indent += 1
        column_counter += 1
        header_row += add_indents(indent)
        header_row += '<th>' + status_info[x]['label'] + '</th>\n'

        # Standard TestRail Status
        if status_info[x]['id'] < 6:
            status_name = status_info[x]['name'] + '_count'
        # Custom Status
        else:
            status_name = 'custom_status' + str(status_info[x]['id'] - 5) + '_count'
        status_count = run_details[status_name]

        status_percent = 100 * status_count / float(total_results)
        status_percent_string = '%.1f' % status_percent
        data_row += add_full_element('td', indent,
                                     status_percent_string + '% (' + str(status_count) + '/' + str(total_results) + ')')

    # Add empty row elements to fill row if needed
    if column_counter < 5:
        for x in range(5 - column_counter):
            header_row += add_full_element('th', indent)
            data_row += add_full_element('td', indent)

    # Add closing elements to table
    indent -= 1
    header_row += close_element('tr', indent)
    data_row += close_element('tr', indent)

    status_html += header_row
    status_html += data_row

    indent -= 1
    status_html += close_element('table', indent)

    indent -= 1
    status_html += close_element('div', indent)

    return status_html


def create_sections(indent):
    try:
        method_uri = 'get_sections/' + str(project_id)
        section_data = client.send_get(method_uri)

        section_html = ''
        first_section_index = 0
        latest_depth_level = 0
        latest_depth_string = ''

        section_details = {}
        for section_entry in section_data:
            # Build dict of needed section details
            section_details[section_entry['id']] = {}
            section_details[section_entry['id']]['display_order'] = section_entry['display_order']
            section_details[section_entry['id']]['depth'] = section_entry['depth']
            section_details[section_entry['id']]['parent_id'] = section_entry['parent_id']
            section_details[section_entry['id']]['is_empty'] = True
            section_details[section_entry['id']]['has_table'] = False
            section_details[section_entry['id']]['name'] = section_entry['name']
            section_details[section_entry['id']]['html'] = ''

            # Create section prefix such as 1.3
            if section_entry['depth'] == 0:
                first_section_index += 1
                latest_depth_level = 0
                latest_depth_string = str(first_section_index)
            elif section_entry['depth'] > 0:
                if section_entry['depth'] > latest_depth_level:
                    latest_depth_level += 1
                    latest_depth_string += '.1'
                else:
                    latest_depth_level = section_entry['depth']
                    # Split the prefix into an array of strings
                    temp_depth_array = latest_depth_string.split('.')
                    temp_depth_array[section_entry['depth']] = str(int(temp_depth_array[-1]) + 1)
                    latest_depth_string = '.'.join(temp_depth_array[0:section_entry['depth'] + 1])

            temp_string = ''
            temp_string += latest_depth_string + ' '
            temp_string += section_entry['name']

            section_details[section_entry['id']]['html'] = add_full_element('h2', indent, temp_string)

        # Compile a dict of case_IDs and Section IDs
        case_sections = get_cases_by_section(project_id)

        # Compile a dict of test_id with corresponding details
        test_details = get_tests_in_run(RUN_ID)

        # Determine each test_id's section
        for test_id in test_details:
            test_case_id = test_details[test_id]['case_id']
            test_section_id = case_sections[test_case_id]

            if section_details[test_section_id]['is_empty']:
                # Mark section as non-empty
                section_details[test_section_id]['is_empty'] = False
                section_details[test_section_id]['has_table'] = True

                # Add table header rows
                temp_html = ''
                temp_html += open_element('table', indent, 'grid')
                temp_html += open_element('colgroup', indent + 1)
                temp_html += add_full_element('col', indent + 2, None, None, 'width: 75px')
                temp_html += add_full_element('col', indent + 2)
                temp_html += add_full_element('col', indent + 2, None, None, 'width: 110px')
                temp_html += close_element('colgroup', indent + 1)

                temp_html += open_element('tr', indent + 1, 'header')
                temp_html += add_full_element('th', indent + 2, 'ID', )
                temp_html += add_full_element('th', indent + 2, 'Title')
                temp_html += add_full_element('th', indent + 2, 'Status')
                temp_html += close_element('tr', indent + 1)

                section_details[test_section_id]['html'] += temp_html

                # Iterate up through parent sections and mark as not empty
                temp_parent_id = section_details[test_section_id]['parent_id']
                while temp_parent_id:
                    section_details[temp_parent_id]['is_empty'] = False
                    temp_parent_id = section_details[temp_parent_id]['parent_id']

            temp_html = ''
            temp_html += open_element('tr', indent + 1)
            # Add Test ID to table
            temp_html += add_full_element('td', indent + 2, 'T' + str(test_id), 'id')

            # Add Test Title to table
            temp_html += add_full_element('td', indent + 2, test_details[test_id]['title'])

            # Add Status Icon to table
            temp_html += open_element('td', indent + 2, None, 'status')
            status_label = status_styles[test_details[test_id]['status_id']]['label']
            status_style_string = 'background: #' + status_styles[test_details[test_id]['status_id']]['bg_color']
            status_style_string += '; color: #ffffff'
            temp_html += add_full_element('span', indent + 3, status_label, 'statusBox', status_style_string)
            temp_html += close_element('td', indent + 2)

            # Close the table row
            temp_html += close_element('tr', indent + 1)

            section_details[test_section_id]['html'] += temp_html

        # Add each section's html value to section_html
        for section in section_details:
            if not section_details[section]['is_empty']:
                # Close the table element if necessary
                if section_details[section]['has_table']:
                    section_details[section]['html'] += close_element('table', indent)
                section_html += section_details[section]['html']

        return section_html

    except:
        e = sys.exc_info()[0]
        print('Error in create_sections')
        print(vars(e))


# RETURNS: A dict of the following format:
#   [
#       {test_id (integer) :
#           {
#           'title' : (string),
#           'status_id' : (integer),
#           'case_id': (integer)
#           },
#       {test_id (integer): ....},
#       ...
#   ]
def get_tests_in_run(target_run_id):
    try:
        request_uri = 'get_tests/'
        request_uri += str(target_run_id)
        tests_dict = client.send_get(request_uri)

        test_data = {}
        for test in tests_dict:
            test_data[test['id']] = {}
            test_data[test['id']]['title'] = test['title']
            test_data[test['id']]['status_id'] = test['status_id']
            test_data[test['id']]['case_id'] = test['case_id']
        return test_data
    except:
        e = sys.exc_info()[0]
        print('Error in get_tests_in_run')
        print(vars(e))


# RETURNS: A dict of {case_id (integer): section_id (integer)}
def get_cases_by_section(target_project_id):
    try:
        request_uri = 'get_cases/'
        request_uri += str(target_project_id)
        cases_dict = client.send_get(request_uri)
        case_data = {}
        for case in cases_dict:
            case_data[case['id']] = case['section_id']
        return case_data
    except:
        e = sys.exc_info()[0]
        print('Error in get_cases_by_section')
        print(vars(e))


def add_empty_element(element, indent, element_class=None):
    element_string = ''
    element_string += add_indents(indent)
    if element_class:
        element_string += '<' + element + ' class="' + element_class + '"></' + element + '>\n'
    else:
        element_string += '<' + element + '></' + element + '>\n'
    return element_string


def add_full_element(element, indent, element_contents=None, element_class=None, element_style=None):
    element_string = add_indents(indent)
    element_string += '<' + element
    if element_class:
        element_string += ' class="' + element_class + '"'
    if element_style:
        element_string += ' style="' + element_style + '"'
    element_string += '>'
    if element_contents:
        element_string += element_contents
    element_string += '</' + element + '>\n'
    return element_string


def close_element(element, indent):
    element_string = ''
    element_string += add_indents(indent)
    element_string += '</' + element + '>\n'
    return element_string


def open_element(element, indent, element_class=None, element_style=None):
    element_string = add_indents(indent)
    element_string += '<' + element
    if element_class:
        element_string += ' class="' + element_class + '"'
    if element_style:
        element_string += ' style="' + element_style + '"'
    element_string += '>\n'
    return element_string


def add_indents(indent):
    indent_string = ''
    for x in range(indent):
        indent_string += '    '
    return indent_string


def main():
    make_report(RUN_ID)
    print("Report completed.")


if __name__ == '__main__':
    main()

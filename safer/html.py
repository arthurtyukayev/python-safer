from lxml import html
from urllib.parse import parse_qsl, urlencode
import re


def debug_print_element(e):
    print(html.tostring(e).decode('utf-8'))
    print('\n\n\n')


def process_extracted_text(extracted_data):
    if isinstance(extracted_data, list):
        if len(extracted_data) > 1:
            # Joins the list of string together and uses re.sub to remove all unwanted unicode ascii characters.
            return " ".join([re.sub('[\n\t\r\xa0]+', '', x.strip()) for x in extracted_data]).strip()
        elif len(extracted_data) == 0:
            return None
        else:
            if 'none' in extracted_data[0].lower():
                return None
            return extracted_data[0].strip()
    elif isinstance(extracted_data, str):
        if 'none' in extracted_data.lower() or extracted_data.lower() == '':
            return None
        return extracted_data.strip()
    raise ValueError('Unrecognized parsing result.')


def process_final_dictionary(data):
    # There could have been an unexpected result from the HTML and int casting could fail
    # In that case, the value should revert back to a string.
    try:
        data['drivers'] = int(data['drivers'])
    except (TypeError, ValueError) as e:
        data['drivers'] = None
    try:
        data['power_units'] = int(data['power_units'])
    except (TypeError, ValueError) as e:
        data['power_units'] = None
    try:
        data['canada_crashes'] = {
            'tow': int(data['canada_crashes']['tow']),
            'fatal': int(data['canada_crashes']['fatal']),
            'injury': int(data['canada_crashes']['injury']),
            'total': int(data['canada_crashes']['total'])
        }
    except (TypeError, ValueError) as e:
        pass
    try:
        data['united_states_crashes'] = {
            'tow': int(data['united_states_crashes']['tow']),
            'fatal': int(data['united_states_crashes']['fatal']),
            'injury': int(data['united_states_crashes']['injury']),
            'total': int(data['united_states_crashes']['total'])
        }
    except (TypeError, ValueError) as e:
        pass
    try:
        data['canada_inspections'] = {
            'driver': {
                'out_of_service': int(data['canada_inspections']['driver']['out_of_service']),
                'out_of_service_percent': data['canada_inspections']['driver']['out_of_service_percent'],
                'inspections': int(data['canada_inspections']['driver']['inspections'])
            },
            'vehicle': {
                'out_of_service': int(data['canada_inspections']['vehicle']['out_of_service']),
                'out_of_service_percent': data['canada_inspections']['vehicle']['out_of_service_percent'],
                'inspections': int(data['canada_inspections']['vehicle']['inspections'])
            }
        }
    except (TypeError, ValueError) as e:
        pass
    try:
        data['us_inspections'] = {
            'driver': {
                'out_of_service': int(data['united_states_inspections']['driver']['out_of_service']),
                'out_of_service_percent': data['united_states_inspections']['driver']['out_of_service_percent'],
                'national_average': data['united_states_inspections']['driver']['national_average'],
                'inspections': int(data['united_states_inspections']['driver']['inspections'])
            },
            'vehicle': {
                'out_of_service': int(data['united_states_inspections']['vehicle']['out_of_service']),
                'out_of_service_percent': data['united_states_inspections']['vehicle']['out_of_service_percent'],
                'national_average': data['united_states_inspections']['vehicle']['national_average'],
                'inspections': int(data['united_states_inspections']['vehicle']['inspections']),
            },
            'hazmat': {
                'out_of_service': int(data['united_states_inspections']['hazmat']['out_of_service']),
                'out_of_service_percent': data['united_states_inspections']['hazmat']['out_of_service_percent'],
                'national_average': data['united_states_inspections']['hazmat']['national_average'],
                'inspections': int(data['united_states_inspections']['hazmat']['inspections']),
            },
            'iep': {
                'out_of_service': int(data['united_states_inspections']['iep']['out_of_service']),
                'out_of_service_percent': data['united_states_inspections']['iep']['out_of_service_percent'],
                'national_average': data['united_states_inspections']['iep']['national_average'],
                'inspections': int(data['united_states_inspections']['iep']['inspections']),
            }
        }
    except (TypeError, ValueError) as e:
        pass

    # Formatting Mileage Year to a dictionary
    data['mcs_150_mileage_year'] = {
        'mileage': int(data['mcs_150_mileage_year'].split(' ')[0].replace(',', '')) if data[
            'mcs_150_mileage_year'] else None,
        'year': int(data['mcs_150_mileage_year'].split(' ')[1].replace('(', '').replace(')', '')) if data[
            'mcs_150_mileage_year'] else None
    }

    # HTML Returns -- for the Duns number when it should just be None or blank
    data['duns_number'] = data['duns_number'] if data['duns_number'] != '--' else None
    return data


def process_search_result_html(tree):
    """
        Parses the search results from the HTML, the HTML comes in as an lxml.etree._ElementTree.
        Using xpath the results are extracted and returned in a list of dictionaries.

    :rtype list
    :param tree: lxml.etree._ElementTree Object that contains the HTMl from the page
    :return: List of parsed results
    """

    # List that will be returned
    result_set = []

    # Set of xpaths needed to return specifc values.
    FIELDS = {
        'id': 'th/b/a/@href',
        'name': 'th/b/a/text()',
        'location': 'td/b/text()'
    }

    # Parses every row of the table of search results.
    for item in tree.xpath("//tr[.//*[@scope='rpw']]")[1:]:
        c_name = item.xpath(FIELDS['name'])[0]
        c_id = item.xpath(FIELDS['id'])[0]
        # Formatting the state and city properly
        c_location = item.xpath(FIELDS['location'])[0].title().split(', ')
        c_location = "{}, {}".format(c_location[0], c_location[1].upper())
        # Parsing the USDOT number out of the xpath
        c_id_parsed = parse_qsl(c_id[10:])
        # Getting the Raw HTML.
        c_raw_html = html.tostring(item, pretty_print=True).decode('utf-8')

        result_set.append({
            'name': c_name,
            'id': c_id_parsed[4][1],
            'location': c_location,
            'html': c_raw_html,
            'url': 'http://www.safersys.org/query.asp?{}'.format(urlencode(c_id_parsed))
        })
    return result_set


def process_company_snapshot(tree):
    """
        Parses the Company Snapshot from the HTML, the HTML comes in as an lxml.etree._ElementTree.
        Using xpath the results are extracted and returned a dictionary of data.

    :rtype Dictionary
    :param tree: lxml.etree._ElementTree Object that contains the HTMl from the page
    :return: Parsed values in a dictionary
    """

    general_info_table = tree.xpath('//table')[6]
    us_inspections_table = tree.xpath('//table')[19]
    us_crashes_table = tree.xpath('//table')[20]
    canada_inspections_table = tree.xpath('//table')[21]
    canada_crashes_table = tree.xpath('//table')[22]
    safety_rating_table = tree.xpath('//table')[23]

    FIELDS = {
        'entity_type': 'tr[2]/td/text()',
        'legal_name': 'tr[4]/td/text()',
        'dba_name': 'tr[5]/td/text()',
        'physical_address': 'tr[6]/td/text()',
        'phone': 'tr[7]/td/text()',
        'mailing_address': 'tr[8]/td/text()',
        'usdot': 'tr[9]/td[1]/text()',
        'state_carrier_id': 'tr[9]/td[2]/text()',
        'mc_mx_ff_numbers': 'tr[10]/td[1]/a/text()',
        'duns_number': 'tr[10]/td[2]/text()',
        'power_units': 'tr[11]/td[1]/text()',
        'drivers': 'tr[11]/td[2]/font/b/text()',
        'mcs_150_form_date': 'tr[12]/td[1]/text()',
        'mcs_150_mileage_year': 'tr[12]/td[2]/font/b/text()',
    }

    for item in FIELDS:
        FIELDS[item] = process_extracted_text(general_info_table.xpath(FIELDS[item]))

    # Out of Service Date comes in as a string 'None' if None
    FIELDS['out_of_service_date'] = process_extracted_text(general_info_table.xpath('tr[3]/td[2]/text()'))
    if FIELDS['out_of_service_date'] == 'None':
        FIELDS['out_of_service_date'] = None

    # Getting Operating Status out of HTML, must be done outside of loop because it requires more decisiveness
    if not isinstance(process_extracted_text(general_info_table.xpath('tr[3]/td[1]/text()')), str):
        FIELDS['operating_status'] = process_extracted_text(general_info_table.xpath('tr[3]/td[1]/font/b/text()'))
    else:
        FIELDS['operating_status'] = process_extracted_text(general_info_table.xpath('tr[3]/td[1]/text()'))

    # Getting Operation Classifications from a list of classifications
    # Checks the HTML for all table rows that contain and X next to them
    FIELDS['operation_classification'] = []
    for classification in tree.xpath('//table')[7].xpath(
            "tr[2]/td/table/tr[.//td[@class='queryfield']/text() = 'X']/td/font/text()"):
        FIELDS['operation_classification'].append(classification)
    last_val = tree.xpath('//table')[7].xpath("tr[2]/td[3]/table/tr[5]/td[2]/text()")
    if len(last_val) > 0:
        FIELDS['operation_classification'].append(process_extracted_text(last_val))

    # Parsing out Carrier Operation from the list of types
    # Checks the HTML for all table rows that contain and X next to them
    FIELDS['carrier_operation'] = []
    for operation in tree.xpath('//table')[11].xpath(
            "tr[2]/td/table/tr[.//td[@class='queryfield']/text() = 'X']/td/font/text()"):
        FIELDS['carrier_operation'].append(operation)

    FIELDS['cargo_carried'] = []
    # Parsing out the type of cargo this carrier is authorized or carry
    # Checks the HTML for all table rows that contain and X next to them
    for cargo in tree.xpath('//table')[15].xpath(
            "tr[2]/td/table/tr[.//td[@class='queryfield']/text() = 'X']/td/font/text()"):
        FIELDS['cargo_carried'].append(cargo)

    """ Parsing the data from tables into nested dictionaries. """

    # Parsing the inspections in the United Status
    FIELDS['united_states_inspections'] = {
        'vehicle': {
            'inspections': process_extracted_text(us_inspections_table.xpath('tr[2]/td[1]/text()')),
            'out_of_service': process_extracted_text(us_inspections_table.xpath('tr[3]/td[1]/text()')),
            'out_of_service_percent': process_extracted_text(us_inspections_table.xpath('tr[4]/td[1]/text()')),
            'national_average': process_extracted_text(us_inspections_table.xpath('tr[5]/td[1]/font/text()'))
        },
        'driver': {
            'inspections': process_extracted_text(us_inspections_table.xpath('tr[2]/td[2]/text()')),
            'out_of_service': process_extracted_text(us_inspections_table.xpath('tr[3]/td[2]/text()')),
            'out_of_service_percent': process_extracted_text(us_inspections_table.xpath('tr[4]/td[2]/text()')),
            'national_average': process_extracted_text(us_inspections_table.xpath('tr[5]/td[2]/font/text()'))
        },
        'hazmat': {
            'inspections': process_extracted_text(us_inspections_table.xpath('tr[2]/td[3]/text()')),
            'out_of_service': process_extracted_text(us_inspections_table.xpath('tr[3]/td[3]/text()')),
            'out_of_service_percent': process_extracted_text(us_inspections_table.xpath('tr[4]/td[3]/text()')),
            'national_average': process_extracted_text(us_inspections_table.xpath('tr[5]/td[3]/font/text()'))
        },
        'iep': {
            'inspections': process_extracted_text(us_inspections_table.xpath('tr[2]/td[4]/text()')),
            'out_of_service': process_extracted_text(us_inspections_table.xpath('tr[3]/td[4]/text()')),
            'out_of_service_percent': process_extracted_text(us_inspections_table.xpath('tr[4]/td[4]/text()')),
            'national_average': process_extracted_text(us_inspections_table.xpath('tr[5]/td[4]/font/text()'))
        }
    }

    # Parsing the crashes in the United States
    FIELDS['united_states_crashes'] = {
        'fatal': process_extracted_text(us_crashes_table.xpath('tr[2]/td[1]/text()')),
        'injury': process_extracted_text(us_crashes_table.xpath('tr[2]/td[2]/text()')),
        'tow': process_extracted_text(us_crashes_table.xpath('tr[2]/td[3]/text()')),
        'total': process_extracted_text(us_crashes_table.xpath('tr[2]/td[4]/text()'))
    }

    # Parsing the inspections in Canada
    FIELDS['canada_inspections'] = {
        "vehicle": {
            'inspections': process_extracted_text(canada_inspections_table.xpath('tr[2]/td[1]/text()')),
            'out_of_service': process_extracted_text(canada_inspections_table.xpath('tr[3]/td[1]/text()')),
            'out_of_service_percent': process_extracted_text(canada_inspections_table.xpath('tr[4]/td[1]/text()'))
        },
        "driver": {
            'inspections': process_extracted_text(canada_inspections_table.xpath('tr[2]/td[2]/text()')),
            'out_of_service': process_extracted_text(canada_inspections_table.xpath('tr[3]/td[2]/text()')),
            'out_of_service_percent': process_extracted_text(canada_inspections_table.xpath('tr[4]/td[2]/text()'))
        },
    }

    # Parsing the crashes in Canada
    FIELDS['canada_crashes'] = {
        'fatal': process_extracted_text(canada_crashes_table.xpath('tr[2]/td[1]/text()')),
        'injury': process_extracted_text(canada_crashes_table.xpath('tr[2]/td[2]/text()')),
        'tow': process_extracted_text(canada_crashes_table.xpath('tr[2]/td[3]/text()')),
        'total': process_extracted_text(canada_crashes_table.xpath('tr[2]/td[4]/text()')),
    }

    # Parsing the Safety Rating
    FIELDS['safety_rating_date'] = process_extracted_text(safety_rating_table.xpath('tr[2]/td[1]/text()'))
    FIELDS['safety_review_date'] = process_extracted_text(safety_rating_table.xpath('tr[2]/td[2]/text()'))
    FIELDS['safety_rating'] = process_extracted_text(safety_rating_table.xpath('tr[3]/td[1]/text()'))
    FIELDS['safety_type'] = process_extracted_text(safety_rating_table.xpath('tr[3]/td[2]/text()'))

    # Parsing the latest update date.
    FIELDS['latest_update'] = process_extracted_text(tree.xpath("//b/font[@color='#0000C0']/text()")[-1])

    FIELDS = process_final_dictionary(FIELDS)
    return FIELDS

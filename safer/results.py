from datetime import datetime
from json import dumps
from webbrowser import open
from dateutil import parser
from safer.api import api_call_get_usdot
from safer.crawler import parse_html_to_tree
from safer.html import process_company_snapshot
import re


class Company:
    """
        Company Object Representation of a Company Snapshot from the SAFER website.
    """

    def __init__(self, data):
        """
        Initializes data coming from the web scraper.

        :param data: Dictionary of values that have been scraped from the CompanySnapshot website.
        """

        # Mapping values.
        self.__entity_type = data['entity_type']
        self.__operating_status = data['operating_status']
        self.__legal_name = data['legal_name']
        self.__dba_name = data['dba_name']
        self.__duns_number = data['duns_number']
        self.__state_carrier_id = data['state_carrier_id']
        self.__mailing_address = data['mailing_address']
        self.__physical_address = data['physical_address']
        self.__carrier_operation = data['carrier_operation']
        self.__mcs_150_mileage_year = data['mcs_150_mileage_year']
        self.__mc_mx_ff_numbers = data['mc_mx_ff_numbers']
        self.__operation_classification = data['operation_classification']
        self.__power_units = data['power_units']
        self.__drivers = data['drivers']
        self.__usdot = data['usdot']
        self.__phone_number = data['phone']
        self.__safety_rating = data['safety_rating']
        self.__safety_type = data['safety_type']
        self.__united_states_inspections = data['united_states_inspections']
        self.__united_states_crashes = data['united_states_crashes']
        self.__canada_inspections = data['canada_inspections']
        self.__canada_crashes = data['canada_crashes']
        self.__cargo_carried = data['cargo_carried']

        # Parsing date strings as datetime objects
        self.__latest_update = datetime.strptime(data['latest_update'], "%m/%d/%Y") if data['latest_update'] else None
        self.__safety_rating_date = datetime.strptime(data['safety_review_date'], "%m/%d/%Y") if data[
            'safety_review_date'] else None
        self.__safety_review_date = parser.parse(data['safety_review_date']) if data[
            'safety_review_date'] else None
        self.__mcs_150_form_date = parser.parse(data['mcs_150_form_date']) if data[
            'mcs_150_form_date'] else None
        self.__out_of_service_date = parser.parse(data['out_of_service_date']) if data[
            'out_of_service_date'] else None

        # Keeping the raw dictionary for dumping to JSON if needed.
        self.__raw = data

        # Building a url for this Company
        self.__url = 'http://www.safersys.org/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&original_query_param=NAME&query_string={}'.format(
            self.__usdot)
        self.__raw['url'] = self.__url

    @property
    def safety_review_data(self):
        return self.__safety_review_date

    @property
    def safety_rating_date(self):
        return self.__safety_rating_date

    @property
    def safety_rating(self):
        return self.__safety_rating

    @property
    def mcs_150_mileage_year(self):
        return self.__mcs_150_mileage_year

    @property
    def phone_number(self):
        return self.__phone_number

    @property
    def cargo_carried(self):
        return self.__cargo_carried

    @property
    def canada_inspections(self):
        return self.__canada_inspections

    @property
    def canada_crashes(self):
        return self.__canada_crashes

    @property
    def usdot(self):
        return self.__usdot

    @property
    def drivers(self):
        return self.__drivers

    @property
    def power_units(self):
        return self.__power_units

    @property
    def united_states_inspections(self):
        return self.__united_states_inspections

    @property
    def operation_classification(self):
        return self.__operation_classification

    @property
    def mc_mx_ff_numbers(self):
        return self.__mc_mx_ff_numbers

    @property
    def mcs_150_form_date(self):
        return self.__mcs_150_form_date

    @property
    def carrier_operation(self):
        return self.__carrier_operation

    @property
    def mailing_address(self):
        return self.__mailing_address

    @property
    def physical_address(self):
        return self.__physical_address

    @property
    def entity_type(self):
        return self.__entity_type

    @property
    def operating_type(self):
        return self.__entity_type

    @property
    def out_of_service_date(self):
        return self.__out_of_service_date

    @property
    def legal_name(self):
        return self.__legal_name

    @property
    def dba_name(self):
        return self.__dba_name

    @property
    def duns_number(self):
        return self.__duns_number

    @property
    def latest_update(self):
        return self.__latest_update

    @property
    def state_carrier_id(self):
        return self.__state_carrier_id

    @property
    def url(self):
        return self.__url

    def __eq__(self, other):
        """
            Compares two Companies
        """
        return self.__usdot == other.__usdot

    def __str__(self):
        return "<Company {} ({}) from  {}>".format(self.__legal_name, self.__usdot, self.__physical_address)

    def __repr__(self):
        return "Company({})".format(self.__usdot)

    def to_json(self):
        return dumps(self.__raw)

    def to_dict(self):
        return self.__raw

    def open_url(self):
        open(self.__url)


class SearchResult:
    """
        A search result object representing the data that is listed when a search is made.
    """

    def __init__(self, result):
        self.__result_id = result['id']
        self.__result_name = result['name']
        self.__result_location = result['location']
        self.__result_raw_html = result['html']
        self.__result_url = result['url']

    @property
    def usdot(self):
        """ ID field of the object is just the USDOT number """
        return self.__result_id

    @property
    def name(self):
        return self.__result_name

    @property
    def location(self):
        return self.__result_location

    @property
    def raw_html(self):
        return re.sub('[\n\t\r\xa0]+', '', self.__result_raw_html)

    @property
    def url(self):
        return self.__result_url

    def __eq__(self, other):
        """
            Compares two search result objects
        """
        return self.__result_id == other.__result_id

    def __str__(self):
        return "<SearchResult {} ({}) from  {}>".format(self.__result_name, self.__result_id, self.__result_location)

    def __repr__(self):
        return "SearchResult({})".format(self.__result_id)

    def get_company_snapshot(self):
        """
        Uses the __result_id value to get the rest of the company data.

        :return: Company Class representing the full company data
        """
        r = api_call_get_usdot(self.__result_id)
        return Company(
            data=process_company_snapshot(
                parse_html_to_tree(r.text)
            )
        )


class SearchResultSet:
    """
        Object representing a list of results, used mainly to iterate through the results.
    """

    def __init__(self, results, search_query):
        self.__search_results = [SearchResult(x) for x in results]
        self.__index = -1
        self.__search_query = search_query
        self.__truncated = True if len(results) > 500 else False
        self.__total_results = len(results)

    @property
    def search_query(self):
        return self.__search_query

    @property
    def is_truncated(self):
        return self.__truncated

    def __len__(self):
        return self.__total_results

    def __getitem__(self, item):
        try:
            return self.__search_results[item]
        except IndexError as e:
            raise IndexError('No value at index {}'.format(item))

    def __iter__(self):
        return self

    def __next__(self):
        self.__index += 1
        if self.__index == len(self.__search_results):
            raise StopIteration
        return self.__search_results[self.__index]

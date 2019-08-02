from safer.api import api_call_search, api_call_get_usdot, api_call_get_mcmx
from safer.crawler import parse_html_to_tree
from safer.html import process_search_result_html, process_company_snapshot
from safer.results import Company, SearchResultSet
from safer.exceptions import CompanySnapshotNotFoundException, SAFERUnreachableException


class CompanySnapshot:
    def __init__(self):
        pass

    @staticmethod
    def search(name):
        """
        Searches the CompanySnapshot using a name,

        :param name: A company name.
        :return: SearchResultSet Class with multiple SearchResults.
        """
        if name == '':
            raise ValueError("'name' parameter must not be empty")

        # Make request
        r = api_call_search(name)
        if r.status_code > 499:
            raise SAFERUnreachableException('The SAFER website is currently unreachable.')
        # Parse HTML result to tree
        tree = parse_html_to_tree(r.text)
        if not len(tree):
            # Parsing will return an empty return set if there are no results
            return SearchResultSet([], name)
        # Parse out values from HTML tree
        search_results = process_search_result_html(tree)
        return SearchResultSet(search_results, name)

    @staticmethod
    def get_by_mc_mx_number(number):
        """
        Gets the Company Snapshot of a given MC/MX Number.

        :param number: MC/MX Number
        :return: Company Class.
        """
        if isinstance(number, str):
            raise ValueError("parameter 'number' must be an int.")

        r = api_call_get_mcmx(mcmx=number)
        if r.status_code > 499:
            raise SAFERUnreachableException('The SAFER website is currently unreachable.')
        # Parse HTML result to tree
        tree = parse_html_to_tree(r.text)
        if not tree:
            # Parsing will return an empty return set if there are no results
            raise CompanySnapshotNotFoundException('The MC or MX number you provided was not found.')
        # Parse out values from HTML tree
        search_results = process_search_result_html(tree)
        pass

    @staticmethod
    def get_by_usdot_number(number):
        """
        Gets the Company Snapshot of a given USDOT Number.

        :rtype: Company
        :param number: USDOT Number
        :return: Company class
        """
        if isinstance(number, str):
            raise ValueError("parameter 'number' must be an int.")

        r = api_call_get_usdot(usdot=number)
        if r.status_code > 499:
            raise SAFERUnreachableException('The SAFER website is currently unreachable.')
        # Parse HTML result to tree
        tree = parse_html_to_tree(r.text)
        if not tree:
            # Parsing will return an empty return set if there are no results
            raise CompanySnapshotNotFoundException('The USDOT number provided was not found.')
        # Parse out values from HTML tree
        search_results = process_company_snapshot(tree)
        return Company(
            data=search_results
        )

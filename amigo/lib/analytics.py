#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   analytics.py
#
#   This class does the intel to the data retrieved from GCP.
#


import util


class Analytics():

    def __init__(self, reports_path, previous_reports_path):

        # These are used to save the new fetched report and to retrieve the previous one.
        self.report_list = util.list_files_in_dir(reports_path , "*.json")
        self.previous_report_list = util.list_files_in_dir(previous_reports_path, "*.json")

        # These are used to check new projects/resources.
        self.report_names = set()
        self.previous_report_names = set()

        self.rules_file = "./rules.yaml"


    ##############################################################################
    #                                                                            #
    #   The first heuristics is to extract any diff in the resources' reports.   #
    #                                                                            #
    ##############################################################################
    def _parse_jsondiff_reports(self, diff):
        """
            Parse jsondiff diff strings to prettify it.
        """
        diff_report = []
        original_str_list = ["$update", "$delete", "$insert"]

        def _parser(original_str):

            # Strings come from jsondiff repors in the "$update" format.
            pretty_str = original_str.strip("$").title()

            if original_str in diff:
                new_list = diff[original_str]

                for item in new_list:
                    diff_report.append("{0} resource: {1}".format(pretty_str, item))


        for original_str in original_str_list:
            _parser(original_str)

        return diff_report


    def _generate_diff_projects_report(self, resource, attribute, diff, data):
        """
            Create a report for every diff found in the resources' reports.
        """
        return {
                    "name":"Difference in Resources",
                    "resource":resource,
                    "attribute":attribute,
                    "diff":self._parse_jsondiff_reports(diff),
                    "gcp_full_report":data
                 }


    def _retrieve_reports_to_be_compared(self, report_file):
        """
            Loop over the previous reports to find the current report
            and retrieve and return this data.
        """
        for previous_report_path in self.previous_report_list:

                previous_report_file = util.get_basename_file(previous_report_path)

                if report_file == previous_report_file:
                    previous_data = util.read_json_file(previous_report_path)

                    return previous_data, previous_report_file

        return None, None


    def check_diff_projects(self):
        """
            Load every current and previous attribute reports and
            creates a report if any diff is found.
        """
        results = []

        for report_path in self.report_list:

            report_file = util.get_basename_file(report_path)
            self.report_names.add(report_file)

            resource, attribute = util.extract_resource_info(report_file)

            data = util.read_json_file(report_path)
            previous_data, previous_report_file = self._retrieve_reports_to_be_compared (report_file)

            if previous_data:
                self.previous_report_names.add(previous_report_file)
                diff = util.jsonfy(util.get_diff_dicts(data, previous_data))

                if diff:
                    util.print_to_stdout("Found diff for {0} in {1}.".format(attribute, resource), color="green")
                    results.append(self._generate_diff_projects_report(resource, attribute, diff, data))

        return results


    ######################################################################################
    #                                                                                    #
    #   The second heuristics is to simply check whether a resource was added/removed.   #
    #                                                                                    #
    ######################################################################################
    def _generate_number_projects_report(self, resource, attribute):
        """
            Returns the JSON report for difference in number of projects.
        """
        return {
                    "name":u"Number of Resources has changed",
                    "resource":resource,
                    "attribute":attribute
                 }


    def check_number_projects(self):
        """
            Check whether a project was created/removed.
        """
        new_projects = self.report_names.symmetric_difference(self.previous_report_names)

        results = []

        if new_projects:

            for project_path in new_projects:
                resource, attribute = util.extract_resource_info(project_path)
                results.append(self._generate_number_projects_report(resource, attribute))

            util.print_to_stdout("Before there were {0} resources being reported, now there are {1}.".format(\
                             len(self.previous_report_names), len(self.report_names)), color="green")

        return results


    #############################################################################################
    #                                                                                           #
    #   The third heuristics is checking every rules violation against the resource's reports.  #
    #                                                                                           #
    #############################################################################################
    def _generate_violation_rules_report(self, project, resource, violation):
        """
            Create a report for every custom rule triggered from the
            resources' reports.
        """
        return {
                    "name":u"Violation for {0} in {1}".format(resource, project),
                    "resource":resource,
                    "project":project,
                    "violation":violation,
                 }


    def _get_resources_list(self, resource_name):
        """
            Search for a all the reports for a given resource,
            loading and returning them in a list.
        """
        resources_list = []

        for report_path in self.report_list:

            project, resource = util.extract_resource_info(util.get_basename_file(report_path))

            if resource_name == resource:
                resources_list.append([project, util.read_json_file(report_path)])

        return resources_list


    def _parse_firewall_value(self, resource_data, rule_items):
        """
            Parse custom rules and check the resource data, returning any violation.
        """

        for rule_item in rule_items:
            for key, value in rule_item.items():

                try:
                    violation1 =  key == "sourceRanges" and any(n in value for n in resource_data["sourceRanges"])
                    print 'hit sourcerange ', key, value, resource_data["sourceRanges"][0]

                    violation2 =  key == "IPProtocol" and any(n in value for n in resource_data["allowed"][0]["IPProtocol"])
                    print 'hit IPProtocol ', key, value, resource_data["allowed"][0]["IPProtocol"]

                    violation3 = key == "ports" and any(n in value for n in resource_data['allowed'][1]['ports'])
                    print 'hit ports ', key, value, resource_data['allowed'][2]['ports']

                except (KeyError, IndexError, TypeError) as e:
                    pass

        return violation1 or violation2 or violation3


    def _do_keyvalue_rule(self, rule_name, rule):
        """
            A key-value rule is simple a rule that checks whether a
            given value is in the resources' report, given its key.
        """
        try:
            resource = rule["violation_resource"]
            rule_items = rule["violation"]

        except KeyError:
            util.print_to_stderr("Rule {0} is ill-formatted in the {1}.".format(rule_name, self.rules_file))

        resources_list = self._get_resources_list(resource)

        results = []

        for project, resource_data in resources_list:

            # To do  add other types of rules besides firewall.
            if resource == "firewalls":
                if self._parse_firewall_value(resource_data, rule_items):
                    results.append(self._generate_violation_rules_report(project, resource_data))

        return results


    def check_custom_rules(self):
        """
           Load custom rules from rules.yaml files check every rule
           violation over every resources' report.
        """
        results = []
        rules = util.read_yaml_file(self.rules_file)

        try:
            for rule_name, rule in rules.items():

                if util.get_value(rule, "rule_type") == "key_value":

                    # All types of rules go here.
                    result = self._do_keyvalue_rule(rule_name, rule)
                    if result:
                        results.append(result)

        except AttributeError:
            util.print_to_stdout("Rule file ('{0}') is ill-formatted.".format(self.rules_file))


        return results


    #############################################################################
    #                                                                           #
    #   The fourth heuristics check whether any warning was generated.          #
    #                                                                           #
    #############################################################################
    def _generate_warnings_report(self, warning):
        """
            Create a report for every custom rule triggered from the
            resources' reports.
        """
        return {
                 "name":u"Warning when Running Amigo",
                  "warnings":warning
                }


    def check_warnings(self, warnings):
        """
            Generate a report if any warning was created during Amigo.
        """
        results = []

        for warning in warnings:
            results.append(self._generate_warnings_report(warning))

        return results

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   menu.py
#
#   Entry point and CLI for Amigo.
#


from lib.reporter import Reporter
from lib.analytics import Analytics
from lib.util import read_config_file, save_to_json_file, print_to_stdout


# TODO: Add CLI with ArgParse
# SETEC-1480


def main():

    config = read_config_file()

    ######################################################
    #                                                    #
    #   Step 1: Fetch all resources' reports from GCP.   #
    #                                                    #
    ######################################################

    reporter = Reporter(config)
    reports, previous_reports = reporter.run()


    ######################################################
    #                                                    #
    #   Step 2: Fetch all resources' reports from GCP.   #
    #                                                    #
    ######################################################

    analyzer = Analytics(reports, previous_reports)

    ### Check for differences in each resource's report.
    diff_project_report = analyzer.check_diff_projects()

    ### Check whether a new project was added/removed.
    new_project_report = analyzer.check_number_projects()

    ### Check each custom rules against each resource's report.
    rules_violation_report = analyzer.check_custom_rules()

    ### Check against GCP warnings.
    warning_report = analyzer.check_warnings(reporter.warnings)


    ######################################################
    #                                                    #
    #   Step 3: Save results to a final JSON report.     #
    #                                                    #
    ######################################################
    results = diff_project_report + new_project_report + rules_violation_report + warning_report


    for result in results:
        save_to_json_file(result, reporter.results, mode="a")

    print_to_stdout("Results for {0} resources were saved to {1}. Exiting...".format(len(analyzer.report_names), \
                                    reporter.results), color="green")



if __name__ == '__main__':
    main()
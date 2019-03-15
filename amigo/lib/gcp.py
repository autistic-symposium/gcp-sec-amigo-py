#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   gcp.py
#
#   Class for all the GCP methods used in Amigo.
#

import util
from oauth2client.file import Storage
from oauth2client.client import GoogleCredentials, ApplicationDefaultCredentialsError
from googleapiclient import discovery, errors


class GCPWrapper():

    def __init__(self, config, entity, version):

        self.config = config
        self.entity = entity
        self.version = version

        self.service = self._get_gcp_service()

        self.warnings = []


    def _auth(self):
        """
            Authenticate Amigo on GCP, fetching the credentials and saving it to
            a local file that can be used for the service discovery.
        """

        # Set the credentials to be used by amigo
        local_cred_file = util.get_value(self.config, "local_cred_file")

        try:
            self.auth = Storage(local_cred_file)
            if util.is_file(util.get_value(self.config, "key_file")):
                creds = GoogleCredentials.get_application_default()
                self.auth.put(creds)
                return True

        except IOError:
            util.print_to_stderr("Cannot open {0} to write, ensure you are running as root. ".format(local_cred_file))

        except ApplicationDefaultCredentialsError:
            util.print_to_stderr("Cannot authenticate to GCP.")

        return False


    def _get_gcp_service(self):
        """
            Start GCP API service.
        """
        if self._auth():
            return discovery.build(self.entity, self.version, credentials=self.auth.get(), cache_discovery=False)

        util.print_to_stderr("Could not start GCP API service. Exiting...")


    def fetch_attribute(self, attribute, project=None):
        """
            Fetch a given attribute for the organization. These attributes are
            activated in the config file, e.g. networks, firewalls, etc.
        """

        api = util.get_method_attribute(self.service, attribute)

        try:

            if project:
                request = api.list(project=project)

            else:
                request = api.list()

        except AttributeError:
            util.print_to_stderr("Could not retrieve data from GCP. Check authentication.")


        attribute_list = []

        try:
            while request:

                response = request.execute()

                # Projects are not really attributes,
                # but they are fetched in the same way.
                if attribute == "projects":
                    for item in response[attribute]:
                        if item["lifecycleState"] != "DELETE_REQUESTED":
                            attribute_list.append(item)

                else:
                    for item in response["items"]:
                        attribute_list.append(item)

                try:
                    request = api.list_next(previous_request=request, previous_response=response)

                except AttributeError:
                    # It starts lopping inside the items, so stop.
                    request = None

        except errors.HttpError as e:
            # Sometimes the response returns some error, so log it and add to the warnings list.
            err = str(e).strip("><")
            util.print_to_stdout("Error while requesting {0}: {1}".format(attribute, err), color="red")
            self.warnings.append(err)

        except KeyError as err:
            # If it starts looping inside undesired objects.
            pass

        return attribute_list

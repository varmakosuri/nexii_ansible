#!/usr/bin/env python

"""This script is to copy the builds from artifactory to setups.\
Script will take the IPs from setup_details.yaml file or from the\
user and checks accessibility  and copies the builds to all accessible setups"""
import subprocess
import os
import re
import paramiko
from scp import SCPClient
import yaml
import wget


class Buildcopy():
    "class to copy builds"

    def __init__(self):
        self.pingableip = []
        self.not_pingableip = []
        self.ipuser = []
        self.password = [
            "Mi@Dim7T",
            "Mi@Dim7T1",
            "Mi@Dim7T2",
            "Mi@Dim8T",
            "Mi@Dim8T1",
            "Mi@Dim8T2"]
        self.director_package = ""
        self.sms_packege = ""
        self.build_url_sms = ""
        self.build_url_sms = ""
        self.build_url_director = ""
        self.dir_pingableip = []
        self.auth_ips = []
        self.path = r"/tmp/build_copy_script/setup_details.yaml"

    def sms_url(self):
        "validate SMS build URL and return URL"
        while True:
            self.build_url_sms = raw_input(
                "Please enter BUILD URL for SMS    : ")

            if not (self.build_url_sms.startswith(
                    'http://artifactory') or ('https://artifactory')):
                print "\nPlease enter a valid URL"
                continue
            if not self.build_url_sms.endswith(
                    'management-server-package.tar'):
                print "\nPlease enter a valid URL"
                continue
            else:
                return self.build_url_sms

    def director_url(self):
        "validate director build URL return URL"
        while True:
            self.build_url_director = raw_input(
                "Please enter BUILD URL for DIRECTOR    : ")
            if not (self.build_url_sms.startswith(
                    'http://artifactory') or ('https://artifactory')):
                print "\nPlease enter a valid URL"
                continue
            if not self.build_url_director.endswith(
                    "director-firmware-package.tar"):
                print "\nPlease enter a valid URL"
                continue
            else:
                return self.build_url_director

    def setup(self):
        "Taking inputs from USER or loading setup information from YAML file"
        while True:
            setup_selection = raw_input(
                "\nPlease enter \"yes\" to copy the builds to the available setups in \"setup_details.yaml\" and  \"no\"to manually enter the setup details : ")
            setup_selection = setup_selection.lower()
            if setup_selection == "yes":
                with open(self.path, "r") as setup_data:
                    data = yaml.load(setup_data)
                    ips = data.get("setup").values()
                return ips

            elif setup_selection == "no":
                while True:
                    user_data = raw_input(
                        "\nEnter \"c\" to enter setup IPs \"q\" to quit :")
                    user_data = user_data.lower()
                    if user_data == "c":
                        value = raw_input(
                            "\nPlease enter setup ip to copy the BUILD  : ")
                        while True:
                            match = re.match(
                                "^(\d{0,3})\.(\d{0,3})\.(\d{0,3})\.(\d{0,3})$", value)
                            if match:
                                self.ipuser.append(value)
                                break

                            else:
                                value = raw_input(
                                    "\nPlease enter the a valid ip address : ")
                                continue
                    elif user_data == "q":
                        return self.ipuser
                        break

    def check_ping(self, ip_list):
        "checking ips accessibility and validating the IPs"
        print "checking ips acessibility......"
        for i in ip_list:
            ping_command = "ping -c 5 -n -W 4 " + i
            (output,
             error) = subprocess.Popen(ping_command,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=True).communicate()
            if len(output) > 200:
                print i, 'is up!'
                self.pingableip.append(i)
            else:
                print i, "is down!"
                self.not_pingableip.append(i)
        if self.not_pingableip:
            print "Following IPs are accessable {0}".format(self.pingableip)
            print "Below IPs are not accessible {0} Please check manually".format(self.not_pingableip)
        else:
            print "Following IPs are accessable {0}".format(self.pingableip)
        return self.pingableip

    def director_build_copy(self, build_url_directors):
        "Copy director build to all the setups"
        if self.dir_pingableip:
            print "\nCopying DIRECTOR tar to all accessible setups {0}".format(self.pingableip)
            self.director_package = build_url_directors.split("/")[-1]
            if self.director_package in os.listdir("/tmp/build_copy_script"):
                obj.build_setup_copy(
                    self.dir_pingableip, self.director_package)

            else:
                print "\nDownloading director package {0}".format(self.director_package)
                try:
                    wget.download(build_url_directors)
                    obj.build_setup_copy(
                        self.dir_pingableip, self.director_package)
                except Exception as err:
                    print "downloading Build from provided URL is failed"

    def sms_build_copy(self, build_url_sms):
        "Copy SMS build to all the setups"
        # print "\nCopying SMS tar package to accessible setups
        # {0}".format(self.pingableip)
        self.sms_packege = build_url_sms.split("/")[-1]
        if self.sms_packege in os.listdir("/tmp/build_copy_script"):
            obj.build_setup_copy(ips_active, self.sms_packege)

        else:
            # wget_builds(self.build_url_sms,build_url_directors)
            print "\ndownloading SMS package {0}".format(self.sms_packege)
            try:
                wget.download(build_url_sms)
                obj.build_setup_copy(ips_active, self.sms_packege)
            except Exception as err:
                print "downloading Build from provided URL is failed"

    def build_setup_copy(self, pingable_ip, package):
        "validate the scp and copy the builds"
        self.dir_pingableip = pingable_ip[:]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ip_var = len(pingable_ip)
        for i in pingable_ip:
            tem_var = 0

            for j in self.password:
                try:
                    ssh.connect(i, 22, "service", j)
                    break
                except Exception as err:
                    #                    if err:
                    tem_var = tem_var + 1
                    if tem_var == len(self.password):
                        print "\nNone of the default authentication worked please check manually for {0}".format(i)
                        self.dir_pingableip.remove(i)
                        break
                    else:
                        continue
            if tem_var != len(self.password):
                with SCPClient(ssh.get_transport()) as scp:
                    print "\nBuild copy is in progress for {0}".format(i)
                    print "." * 20
            # package1='/tmp/build_copy_script/'+package
                    try:
                        scp.put("/tmp/build_copy_script/" + package, '/tmp/')
                        print "\n{0} copy is  complted to {1}/tmp".format(package, i)
                    except Exception as err:
                        print "unable to SCP to setup{0} with error{1}".format(i, err)
            else:
                if ip_var == 0:
                    print "All setup Authentication failed"
                    break
                else:
                    ip_var = ip_var - 1
                    continue


obj = Buildcopy()
sms_url_from_user = obj.sms_url()
dir_url_from_user = obj.director_url()
setup_details = obj.setup()
ips_active = obj.check_ping(setup_details)
obj.sms_build_copy(sms_url_from_user)
obj.director_build_copy(dir_url_from_user)
# obj.build_setup_copy(b)

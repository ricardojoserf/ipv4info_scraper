#!/usr/bin/python3
import subprocess
import requests
import argparse
import requests
import time
import sys
import csv
import os
import sys
from bs4 import BeautifulSoup
import distutils.spawn


ipv4_base_url = "http://ipv4info.com"


def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--companies_file', required=False, default=None, action='store', help='File with ranges to analyze')
	parser.add_argument('-C', '--companies_list', required=False, default=None, action='store', help='Comma separated list of companies')
	parser.add_argument('-o', '--output_directory', required=False, default="res_subdoler", action='store', help='Output directory')
	parser.add_argument('-cf', '--country_filter', required=False, action='store', help='Country filter for the list of IP ranges calculated in IPv4info')
	my_args = parser.parse_args()
	return my_args


def create_directory(output_directory):
		if not os.path.exists(output_directory):
			os.makedirs(output_directory)


def create_file_from_list(list_, fname_, output_directory):
	values_ = list_.split(",")
	fname_ = output_directory+"/"+fname_
	with open(fname_, 'w') as f:
		for item in values_:
			f.write("%s\n" % item)
	return fname_


# Get url from IPv4info
def get_info_url(company_name):
	search_url = ipv4_base_url + "/?act=check&ip="+company_name
	response = requests.get(search_url)
	if response.history:
	    for resp in response.history:
	        return resp.headers['Location']
	else:
		print("Failed to get IPv4info page for that company")
		sys.exit(1)


# Get range in slash notation
def get_ranges(company_name, target_countries=None):
	array_aux = [{'range': 32, 'val': 1}, {'range': 31, 'val': 2}, {'range': 30, 'val': 4}, {'range': 29, 'val': 8}, {'range': 28, 'val': 16}, {'range': 27, 'val': 32}, {'range': 26, 'val': 64}, {'range': 25, 'val': 128}, {'range': 24, 'val': 256}, {'range': 23, 'val': 512}, {'range': 22, 'val': 1024}, {'range': 21, 'val': 2048}, {'range': 20, 'val': 4096}, {'range': 19, 'val': 8192}, {'range': 18, 'val': 16384}, {'range': 17, 'val': 32768}, {'range': 16, 'val': 65536}, {'range': 15, 'val': 131072}, {'range': 14, 'val': 262144}, {'range': 13, 'val': 524288}, {'range': 12, 'val': 1048576}, {'range': 11, 'val': 2097152}, {'range': 10, 'val': 4194304}, {'range': 9, 'val': 8388608}, {'range': 8, 'val': 16777216}, {'range': 7, 'val': 33554432}, {'range': 6, 'val': 67108864}, {'range': 5, 'val': 134217728}, {'range': 4, 'val': 268435456}, {'range': 3, 'val': 536870912}, {'range': 2, 'val': 1073741824}, {'range': 1, 'val': 2147483648}]
	ranges_info =  []
	info_url = ipv4_base_url + get_info_url(company_name)
	r = requests.get(info_url)
	soup = BeautifulSoup(r.content, 'html.parser')
	for i in soup.findAll('tr'):
		vals = i.findAll('td')
		if len(vals) == 10:
			# ipv4_base_url + "/" + 
			link = str(vals[1])
			first_ip = vals[2].getText()
			last_ip  = vals[3].getText()
			range_size = vals[4].getText()
			asn = vals[6].getText().replace("\n", " ")
			block_name = vals[7].getText()
			organization = vals[8].getText()
			country = ""
			for e in vals[9].findAll('a'):
				country += e.getText() + " "
			range_val = ""
			if "Size" not in range_size:
				for j in array_aux:
					if (int(range_size)-int(j['val'])) <=0:
						range_val = first_ip+"/"+str(j['range'])
						break
			if target_countries is not None and country.split(" ")[0] not in target_countries:
				pass
			else:
				ranges_info.append({'organization': organization, 'block_name': block_name, 'block_start': first_ip, 'block_end': last_ip, 'range_size': range_size, 'asn': asn, 'country': country, 'range': range_val, 'link': link})
	return ranges_info						


# Range Processing and Calculation
def range_extractor(companies_file, country_filter):
	target_countries = None
	if country_filter is not None:
		target_countries = country_filter.split(",")
	if companies_file is not None:
		companies = open(companies_file).read().splitlines()
		for c in companies:
			ranges_info = get_ranges(c, target_countries)
			print(ranges_info)


def main():
	args = get_args()
	companies_file = args.companies_file
	output_directory = args.output_directory
	output_directory = output_directory + "/" if not output_directory.endswith("/") else output_directory
	create_directory(output_directory)	
	if args.companies_list is not None:
		companies_file = create_file_from_list(args.companies_list, "temp_companies", output_directory)
	try:
		country_filter = args.country_filter
		range_extractor(companies_file, country_filter)
	except Exception as e:
		print("Error: %s"%(str(e)))
		

if __name__== "__main__":
	main()
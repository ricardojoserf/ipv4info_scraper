#!/usr/bin/python3
import os
import sys
import time
import json
import requests
import argparse
from bs4 import BeautifulSoup
ipv4_base_url = "http://ipv4info.com"


def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--companies_file',  required=False, default=None, action='store', help='File with companies to analyze')
	parser.add_argument('-C', '--companies_list',  required=False, default=None, action='store', help='Comma separated list of companies')
	parser.add_argument('-f', '--country_filter',  required=False, action='store', help='Country filter for the list of IP ranges calculated in IPv4info')
	parser.add_argument('-o', '--output_file',     required=False, default="output.txt", action='store', help='Output directory')
	parser.add_argument('-d', '--debug',           required=False, default=False, action='store_true', help='Debug mode')
	return parser


# Get url from IPv4info
def get_info_url(company_name):
	search_url = ipv4_base_url + "/?act=check&ip="+company_name
	response = requests.get(search_url)
	if response.history:
		return response.history[0].headers['Location']
	else:
		print("Failed to get IPv4info page for that company")
		sys.exit(1)


# Get domains from /domains-in-block/ IPv4info url
def get_domains(domains_in_block_link,debug):
	if debug: print("[-] Getting domains from block url:  %s"%domains_in_block_link)
	r = requests.get(str(domains_in_block_link))
	soup = BeautifulSoup(r.content, 'html.parser')
	domains_info = []
	for i in soup.findAll('tr'):
		vals = i.findAll('td')
		if len(vals) ==7 and (vals[1].getText() != "ip"):
			ip = vals[1].getText()
			domain =     ' '.join(vals[2].getText().split())
			web_server = ' '.join(vals[3].getText().split())
			powered_by = ' '.join(vals[4].getText().split())
			host_name =  ' '.join(vals[5].getText().split())
			updated_date = ' '.join(vals[6].getText().split())
			domain_info = {'ip':ip,'domain':domain,'web_server':web_server,'powered_by':powered_by,'host_name':host_name,'updated_date':updated_date}
			domains_info.append(domain_info)
	return domains_info


# Get range in slash notation
def get_ranges(company_name, target_countries, debug):
	array_aux = [{'range': 32, 'val': 1}, {'range': 31, 'val': 2}, {'range': 30, 'val': 4}, {'range': 29, 'val': 8}, {'range': 28, 'val': 16}, {'range': 27, 'val': 32}, {'range': 26, 'val': 64}, {'range': 25, 'val': 128}, {'range': 24, 'val': 256}, {'range': 23, 'val': 512}, {'range': 22, 'val': 1024}, {'range': 21, 'val': 2048}, {'range': 20, 'val': 4096}, {'range': 19, 'val': 8192}, {'range': 18, 'val': 16384}, {'range': 17, 'val': 32768}, {'range': 16, 'val': 65536}, {'range': 15, 'val': 131072}, {'range': 14, 'val': 262144}, {'range': 13, 'val': 524288}, {'range': 12, 'val': 1048576}, {'range': 11, 'val': 2097152}, {'range': 10, 'val': 4194304}, {'range': 9, 'val': 8388608}, {'range': 8, 'val': 16777216}, {'range': 7, 'val': 33554432}, {'range': 6, 'val': 67108864}, {'range': 5, 'val': 134217728}, {'range': 4, 'val': 268435456}, {'range': 3, 'val': 536870912}, {'range': 2, 'val': 1073741824}, {'range': 1, 'val': 2147483648}]
	ranges_info =  []
	info_url = ipv4_base_url + get_info_url(company_name)
	if debug: print("\n[+] Getting ranges from company url: %s"%info_url)
	r = requests.get(info_url)
	soup = BeautifulSoup(r.content, 'html.parser')
	if "Querys limit is exceeded" in soup:
		print("Querys limit is exceeded")
		return
	for i in soup.findAll('tr'):
		vals = i.findAll('td')
		if len(vals) == 10:
			link_splitted = str(vals[1]).split('"')
			block_info_path =link_splitted[3] if len(link_splitted) > 3 else ""
			block_info_link = ipv4_base_url + block_info_path if len(link_splitted) > 3 else ""
			domains_in_block_link = block_info_link.replace("block-info","domains-in-block")
			domains_in_block_link = ' '.join(domains_in_block_link.split())
			first_ip = vals[2].getText()
			last_ip  = vals[3].getText()
			range_size = vals[4].getText()
			asn = vals[6].getText().replace("\n", " ")
			block_name = vals[7].getText()
			organization = vals[8].getText()
			country = ""
			for e in vals[9].findAll('a'):
				country += e.getText() + " "
			range_val,domains = "",""
			if "Size" not in range_size and "white-space" not in domains_in_block_link:
				domains = get_domains(domains_in_block_link,debug)
				for j in array_aux:
					if (int(range_size)-int(j['val'])) <=0:
						range_val = first_ip+"/"+str(j['range'])
						break
			if target_countries is not None and country.split(" ")[0] not in target_countries:
				pass
			else:
				ranges_info.append({'organization': organization, 'block_name': block_name, 'block_start': first_ip, 'block_end': last_ip, 'range_size': range_size, 'asn': asn, 'country': country, 'range': range_val, 'block_info_link': block_info_link, 'domains_in_block_link': domains_in_block_link, 'domains': domains })
	return ranges_info


# Call get_ranges() for each company name
def calculate_companies(companies, target_countries,debug):
	try:
		all_ranges = []
		for c in companies:
			ranges_info = get_ranges(c, target_countries,debug)
			all_ranges.append(ranges_info)
		return all_ranges
	except Exception as e:
		print("Error: %s"%(str(e)))


def main():
	parser = get_args()
	args = parser.parse_args()
	if args.companies_file is not None:
		if os.path.isfile(args.companies_file):
			companies = open(args.companies_file).read().splitlines()  
		else:
			print("\n[-] ERROR: File not found\n")
			parser.print_help()
			sys.exit(0)
	elif args.companies_list is not None: 
		companies = args.companies_list.split(",")
	else:
		print("\n[-] ERROR: It is necessary to use -c or -C parameters\n")
		parser.print_help()
		sys.exit(0)
	target_countries = args.country_filter.split(",") if args.country_filter is not None else None
	output_file = args.output_file
	debug = args.debug
	all_ranges = calculate_companies(companies, target_countries,debug)
	print(json.dumps(all_ranges, indent=4, sort_keys=True))
	with open(output_file, 'w') as outfile:
		json.dump(all_ranges, outfile)
		

if __name__== "__main__":
	main()
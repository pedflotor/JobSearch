import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import os
pd.set_option('max_colwidth', 200)

count = 0


# Function to extract the job id from the url
def extract_job_id(jobs_id):
    urls = []

    for jobs_id in jobs_id:
        urls.append(re.findall(r'([0-9]{10})', jobs_id)[0])

    urls = list(map(int, urls))
    return urls


# Function to check if the jobs to be scraped are already on the list
def check_repeated_jobs(new_urls, already_on_list):
    clean_url = []

    for i in range(len(new_urls)):
        # print(i)
        if new_urls[i] in already_on_list:
            print(new_urls[i] in already_on_list, new_urls[i])

        else:
            clean_url.append(new_urls[i])

    # print('New Links', clean_url)
    return clean_url


# Function to scrape the job data from the web. liked_jobs is defined as '1' or '0' depending on if the job to be
# scraped is liked or not
def retrieve_job_data(urls, liked_job):

    # Variables to save the jobs data
    job_like = []
    post_title = []
    company_name = []
    post_date = []
    job_location_city = []
    job_location_region = []
    job_location_country = []
    job_desc = []
    level = []
    emp_type = []
    functions = []
    industries = []
    job_id = []
    link = []

    for urls in urls:
        print('Job_ID to be scraped: ', urls)
        # Make a GET request to fetch the raw HTML content
        job_url = 'https://www.linkedin.com/jobs/view/' + str(urls)
        print(job_url)
        html_content = requests.get(job_url).text

        # Parse the html content
        soup = BeautifulSoup(html_content, "lxml")
        # print(soup.prettify()) # Line used to look on HTML for the data to be scraped

        # job title
        try:
            job_titles = soup.find("h1", class_="topcard__title").text
            job_titles = re.sub("[^a-zA-Z0-9äöüÄÖÜß\s]+", " ", str(job_titles))
            job_titles = re.sub("\s{2,}", " ", str(job_titles))
            post_title.append(job_titles)
        except:
            print('job_titles')
            post_title.append('0')

        # company name
        try:
            company_names = soup.find("a", class_="topcard__org-name-link topcard__flavor--black-link").text
            company_names = re.split("\n+", company_names)
            company_name.append(company_names)
        except:
            print('company_names')
            company_name.append('0')

        # job location
        try:
            job_locations = soup.find("span", class_="topcard__flavor topcard__flavor--bullet").text

            # in case the location specified includes the city, region and country
            if len(job_locations) == 3:
                job_location_city.append(job_locations[len(job_locations) - 3])
                job_location_region.append(job_locations[len(job_locations) - 2])
                job_location_country.append(job_locations[len(job_locations) - 1])

            # in case the location specified includes the region and country
            else:
                job_location_city.append('0')
                job_location_region.append(job_locations[len(job_locations) - 2])
                job_location_country.append(job_locations[len(job_locations) - 1])

        except:
            print('job location')
            job_location_city.append('0')
            job_location_region.append('0')
            job_location_country.append('0')

        # posting date
        try:
            post_dates = soup.find('span', class_="topcard__flavor--metadata posted-time-ago__text").text
            post_date.append(post_dates)
        except:
            print('posting date')
            post_date.append('0')

        # job description
        try:
            job_descs = soup.find("div",
                                class_="show-more-less-html__markup show-more-less-html__markup--clamp-after-5").text
            job_descs = re.sub("[^a-zA-Z0-9äöüÄÖÜß\s]+", " ", str(job_descs))
            job_descs = re.sub("(\s{2,})|(\n+)|(;)", "", str(job_descs))
            job_desc.append(job_descs)
        except:
            print('job description')
            job_desc.append('0')

        # job additional data
        try:
            additional_data_container = []
            for span in soup.find_all('span', class_='job-criteria__text job-criteria__text--criteria'):
                additional_data_container.append(span.text)

            # print(additional_data_container)

            # job level
            level.append(additional_data_container[0])

            # job type
            emp_type.append(additional_data_container[1])

            # job function
            functions.append(additional_data_container[2])

            # job industry
            industries.append(additional_data_container[3])

            # liked job (VARIABLE TO MARK IF A JOB IS ONE THAT YOU LIKE)
            job_like.append(liked_job)

            # linkedin job id
            job_id.append(urls)

            # job url
            link.append(job_url)
        except:
            print('job additional data')
            level.append('0')
            emp_type.append('0')
            functions.append('0')
            industries.append('0')
            job_like.append(liked_job)
            job_id.append(urls)
            link.append(job_url)

    print('The number of scraped jobs is: ', len(post_title))
    print(len(job_like))
    print(len(post_date))
    print(len(company_name))
    print(len(post_title))
    print(len(job_location_city))
    print(len(job_location_region))
    print(len(job_location_country))
    print(len(job_desc))
    print(len(level))
    print(len(emp_type))
    print(len(functions))
    print(len(industries))
    print(len(job_id))
    print(len(link))

    # Create a DataFrame with the scraped data
    job_data = pd.DataFrame({'Liked job?': job_like,
                             'Date': post_date,
                             'Company Name': company_name,
                             'Job Title': post_title,
                             'City': job_location_city,
                             'Region': job_location_region,
                             'Country': job_location_country,
                             'Description': job_desc,
                             'Level': level,
                             'Type': emp_type,
                             'Function': functions,
                             'Industry': industries,
                             'ID': job_id,
                             'Link': link
                             })

    # clean description column
    job_data['Description'] = job_data['Description'].str.replace('\n', ' ')

    return job_data


# Function to update dataframe on an existing csv file
def write_in_existing_file(dataframe_jobs):
    dataframe_jobs.to_csv('ScrapeOfLikedJobs.csv', mode='a', sep='|', header=0, index=False)


# Function to write dataframe on a new csv file
def write_in_new_file(dataframe_jobs):
    dataframe_jobs.to_csv('ScrapeOfLikedJobs.csv', mode='a', sep='|', index=False)


# *******************************************
# List of variables to be defined by the user
# *******************************************


# List of URLs where the text will be scraped from
links = ["https://www.linkedin.com/jobs/view/2354678736",
         "https://www.linkedin.com/jobs/view/2354626591",
         "https://www.linkedin.com/jobs/view/2371914278",
         "https://www.linkedin.com/jobs/view/2389945426",
         "https://www.linkedin.com/jobs/view/2394548047"]

# Define if the jobs specified on the "links" variable is liked (1) or not (0)
is_liked = '1'


# ********************
# Start of the program
# ********************
new_job_ID_list = extract_job_id(links)

if os.path.isfile('ScrapeOfLikedJobs.csv'):
    print("A file already exists. Reading the data...")
    SoLJ = pd.read_csv('ScrapeOfLikedJobs.csv', sep='|')
    index = pd.Index(SoLJ['ID'])
    print("Checking for jobs already on the file...")
    url = check_repeated_jobs(new_job_ID_list, index)

    # In case there is new jobs that are not on the list, then the data is retrieved
    if len(url) != 0:
        print("List of new jobs not found on the existing file: ", url)
        print("Retrieving the job data from the website...")
        job_data = retrieve_job_data(url, is_liked, count)
        print("Writing the new data on the file...")
        write_in_existing_file(job_data)
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(job_data.head(2))

    else:
        print("All links provided contain jobs already on the destination file")
        print("No new data will be writen on the file")


else:
    job_data = retrieve_job_data(new_job_ID_list, is_liked)
    write_in_new_file(job_data)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(job_data.head(2))


# TODO
# 1.Write README
# 2.Clean code and improve comments
# 3.
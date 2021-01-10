import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import os
pd.set_option('max_colwidth', 200)


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
        print(i)
        if new_urls[i] in already_on_list:
            print(new_urls[i] in already_on_list, new_urls[i])

        else:
            clean_url.append(new_urls[i])

    print('New Links', clean_url)
    return clean_url


# Function to scrape the job data from the web. liked_jobs is defined as 'Yes' or 'No' depending on if the job to be
# scraped is liked or not
def retrieve_job_data(urls, liked_job):

    # Variables to save the jobs data
    job_like = []
    post_title = []
    company_name = []
    post_date = []
    job_location = []
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
        print(soup.prettify()) # Line used to look on HTML for the data to be scraped

        # job title
        job_titles = soup.find("h1", class_="topcard__title").text
        post_title.append(job_titles)

        # company name
        company_names = soup.find("a", class_="topcard__org-name-link topcard__flavor--black-link").text
        company_name.append(company_names)

        # job location
        job_locations = soup.find("span", class_="topcard__flavor topcard__flavor--bullet").text
        job_location.append(job_locations)

        # posting date
        post_dates = soup.find('span', class_="topcard__flavor--metadata posted-time-ago__text").text
        post_date.append(post_dates)

        # job description
        job_descs = soup.find("div",
                              class_="show-more-less-html__markup show-more-less-html__markup--clamp-after-5").text
        job_desc.append(job_descs)

        # job additional data
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

    print('The number of scraped jobs is: ', len(post_title))

    # Create a DataFrame
    job_data = pd.DataFrame({'Liked job?': job_like,
                             'Date': post_date,
                             'Company Name': company_name,
                             'Post': post_title,
                             'Location': job_location,
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


# List of URLs where the text will be scraped from
links = ["https://www.linkedin.com/jobs/view/2354678736",
         "https://www.linkedin.com/jobs/view/2354626591",
         "https://www.linkedin.com/jobs/view/2371914278"]


new_job_ID_list = extract_job_id(links)

if os.path.isfile('ScrapeOfLikedJobs.csv'):
    SoLJ = pd.read_csv('ScrapeOfLikedJobs.csv', sep='|')
    index = pd.Index(SoLJ['ID'])
    url = check_repeated_jobs(new_job_ID_list, index)
    print(url)

    try:
        job_data = retrieve_job_data(url, 'Yes')
        write_in_existing_file(job_data)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(job_data.head(2))

    except:
        print('The jobs are already on the list')
        print('********************************')
        print('List of jobs: ')
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(SoLJ.head(2))

else:
    job_data = retrieve_job_data(new_job_ID_list, 'Yes')
    write_in_new_file(job_data)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(job_data.head(2))


# TODO
# 1.Write README
# 2.Clean code and improve comments
# 3.Separate location in city, region and country
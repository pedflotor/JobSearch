# Program to add job data extracted from a website to a csv file

The program will check if the requested job IDs are already included in a csv file and if not the job data will be
extracted and included on it. Also a column will be added to specify if the user likes or not the job post

This program is part of a project that consist on automating the job search according to the job posts that the user liked
previously

### Prerequisites

The program will require the following libraries to be installed:
+ requests 
+ pandas
+ re
+ BeautifulSoup
+ os



### Inputs

Url or list of urls with jobs to be scraped

```
links = ["https://www.linkedin.com/jobs/view/2354678736"]
```




Specify if the job is liked or not

```
is_liked = 'Yes'
```
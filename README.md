# Web Scraping and Knowledge Graphs for Retrieval Augmented Generation
This is a work in progress. Working implementations are
- Spiders
    - `Spiders/Spider.py` (a base implementation of a Scrapy spider - not super useful on its own, but the next one inherits from it which is important to know when making improvements.)
    - `Spiders/HTMLtoMarkdownSpider.py` (This spider is the most advanced, parsing the text by converting it to Markdown and saving links)
- Parsers
    - The parser that I have landed on is in WebsiteToMD, which I run within `Spiders/HTMLtoMarkdownSpider.py` to parse my text.
        - Note that this is actually written in Typescript, and needs to be compiled. Simply run 
        ```bash
        esbuild esbuild.config.mjs production
        ```
        in its own terminal from within the folder and leave it running, and it will recompile after any changes are detected. Note that you need to follow the installation instructions below first.

## Installation
After git cloning this repo to your directory of choice, follow these steps:

1. I recommend you do this in a conda environment as there are many dependencies. If you don't have it installed I'd [download Miniconda here](https://docs.anaconda.com/free/miniconda/index.html#latest-miniconda-installer-links).
2. Open Anaconda Terminal (I use Powershell, on Windows simply search in the start menu
for `Anaconda Powershell Prompt (miniconda)`
3. Navigate to the directory this repo is in and type:
> ```bash
> conda env create -f environment.yml
> ```
This should install all your python dependencies.

To run any of the js projects, navigate to their respective folders in terminal and type:
```bash
npm install
```
which should install the dependencies found in their package.json.
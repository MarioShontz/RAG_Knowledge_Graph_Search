# Web Scraping and Knowledge Graphs for Retrieval Augmented Generation
This is a work in progress. Working implementations are
- Spiders
    - `Spiders/Spider.py` (a base implementation of a Scrapy spider - not super useful on its own, but the next one inherits from it which is important to know when making improvements.)
    - `Spiders/HTMLtoMarkdownSpider.py` (This spider is the most advanced, parsing the text by converting it to Markdown and saving links)
- Parsers
    - The parser that I have landed on is in WebsiteToMD, which I run within `Spiders/HTMLtoMarkdownSpider.py` to parse my text.
- Knowledge Graph
    - `FSU_RAG_Search.ipynb` - This is an `ipython` file that you can open with Jupyter Notebook. see below for how to do that.

## Installation
After git cloning this repo to your directory of choice, follow these steps:

1. I recommend you do this in a conda environment (Conda environments isolate installed packages to only terminals that have the environment activate so that you don't have conflicting dependencies on all your various projects). Start by [downloading Miniconda here](https://docs.anaconda.com/free/miniconda/index.html#latest-miniconda-installer-links). It is easiest to just use the GUI-based installer.
2. Open Anaconda Terminal (on Windows simply search the start menu
for `Anaconda Powershell Prompt (miniconda)`
3. Navigate to the directory this repo is in and type:
> ```bash
> conda env create -f environment.yml
> ```
This should create an environment called fsu_vector_search_env and install all your python dependencies, allowing you to run things in `Spiders/`

To run any of the js projects, navigate to their respective folders in terminal and type:
```bash
npm install
```
which should install the dependencies found in their package.json. For `WebsitetoMD.js`, there is an additionaly step outlined [below](#logic-breakdown-of-main-parts).

To run `FSU_RAG_Search.ipynb`, you'll need to run `conda install jupyter` and press `y` to confirm. See [jupyter.org](https://jupyter.org/) for more info. After installing, in any terminal in the project's root directory, type `jupyter lab`, and it should open a webpage in your browser that functions as an IDE for your `.ipynb` files. From there you can run each cell in `FSU_RAG_Search.ipynb`. Running all will probably take about 20 minutes so take that into account. The output from my last run is saved and shown there so it should all be the same unless you make changes.

## Logic Breakdown of Main Parts
`FSU_RAG_Search.ipynb` is the main point where things come together. The logic in it is fairly straightforward, but some things aren't the most obvious. It currently uses `Spiders/HTMLtoMarkdownSpider.py` to perform scraping, which in turn is using `WebsiteToMD/run.js` to run `main.js`. `main.js` is compiled typescript - to modify it, modify the files in `WebsiteToMD/src` and build using the command
```bash
esbuild esbuild.config.mjs production
```
in its own terminal from within the folder and leave it running, and it will recompile your code after any changes are detected. Note that you should do `npm install` first to install esbuild and the rest of the module's dependencies.

Another thing to note about `WebsiteToMD` is that it currently uses multiple methods to "create" the `WebsiteParser` object, where it would be simpler to just make it. I did this on purpose - in the future, I may want to have different parsing logics for different websites or specific types, such as `.rss` feeds.

## TODO
1. Improve Knowledge Graph curation. The way I see it, this involves predetermining entity types and their attributes and relationship types and their attributes. Then, we can have a language model look for these elements directly in the text. See my diagram below

![Simple Entity-Relationship Diagram of FSU](<img/E-R Diagram FSU.jpg>)
Also, checkout [schema.org](https://www.schema.org) and `schemaorg-current-https.rdf`, which I downloaded from it, for ideas. There are many premade entities and relationships in this, including one for an [educational organization](https://schema.org/EducationalOrganization) [college/university](https://schema.org/CollegeOrUniversity), and more fundamental things like a [person](https://schema.org/Person), [time](https://schema.org/Time), and much more.
2. General improvements to logic for scalability and readability. Need to have clearer path ahead first.
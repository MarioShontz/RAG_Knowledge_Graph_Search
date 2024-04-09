import fetch from 'node-fetch';
import { Readability } from '@mozilla/readability';
import * as DOMPurify from 'isomorphic-dompurify';
import { getBaseUrl } from '../helpers';
import { Parser } from './Parser';
import { parseHtmlContent } from './parsehtml';
const jsdom = require("jsdom")
const { JSDOM } = jsdom
global.DOMParser = new JSDOM().window.DOMParser

type Article = {
    title: string;
    content: string;
    textContent: string;
    length: number;
    excerpt: string;
    byline: string;
    dir: string;
    siteName: string;
    lang: string;
};

class WebsiteParser extends Parser {
    constructor() {
        super();
    }

    test(url: string): boolean {
        return this.isValidUrl(url);
    }

    async prepareNote(url: string): Promise<string> {
        const originUrl = new URL(url);
        const response = await fetch(originUrl.href);
        const textContent = await response.text()
        const document = new DOMParser().parseFromString(textContent, 'text/html');

        //check for existing base element
        const originBasElements = document.getElementsByTagName('base');
        let originBaseUrl = null;
        if (originBasElements.length > 0) {
            originBaseUrl = originBasElements.item(0).getAttribute('href');
            Array.from(originBasElements).forEach((originBasEl) => {
                originBasEl.remove();
            });
        }

        // Set base to allow Readability to resolve relative path's
        const baseEl = document.createElement('base');
        baseEl.setAttribute('href', getBaseUrl(originBaseUrl ?? originUrl.href, originUrl.origin));
        document.head.append(baseEl);
        const cleanDocumentBody = DOMPurify.sanitize(document.body.innerHTML);
        document.body.innerHTML = cleanDocumentBody;

        const previewUrl = this.extractPreviewUrl(document);
        const readableDocument = new Readability(document).parse();

        const articleData = readableDocument?.content
          ? await this.parsableArticle(readableDocument, originUrl.href, previewUrl)
          : await this.notParsableArticle(originUrl.href, previewUrl);
       
        return articleData; // Return the resolved articleData here 
    }

    private async parsableArticle(article: Article, url: string, previewUrl: string | null) {
        const title = article.title || 'No title';
        const siteName = article.siteName || '';
        const author = article.byline || '';
        const content = await parseHtmlContent(article.content);

        let processedContent = "# [%articleTitle%](%articleURL%)\n\nAuthor: %author%\nContent:\n%articleContent%"
            .replace(/%date%/g, this.getFormattedDateForContent())
            .replace(/%articleTitle%/g, title)
            .replace(/%articleURL%/g, url)
            .replace(/%articleContent%/g, content)
            .replace(/%siteName%/g, siteName)
            .replace(/%author%/g, author)
            .replace(/%previewURL%/g, previewUrl || '');

        return processedContent;
    }

    private async notParsableArticle(url: string, previewUrl: string | null) {
        console.error('Website not parseable');

        let content = "This page has no parseable content"
        return content;
    }

    /**
     * Extracts a preview URL from the document.
     * Searches for OpenGraph `og:image` and Twitter `twitter:image` meta tags.
     * @param document The document to extract preview URL from
     */
    private extractPreviewUrl(document: Document) {
        let previewMetaElement = document.querySelector('meta[property="og:image"]');
        if (previewMetaElement == null) {
            previewMetaElement = document.querySelector('meta[name="twitter:image"]');
        }
        return previewMetaElement?.getAttribute('content');
    }
}

export default WebsiteParser;
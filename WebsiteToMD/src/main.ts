import WebsiteParser from './parsers/WebsiteParser';
import ParserCreator from './parsers/ParserCreator';

export default class WebsiteToMD {
    private parserCreator: ParserCreator;

    async onload(): Promise<void> {
        this.parserCreator = new ParserCreator([
            new WebsiteParser(),
        ]);
    }

    async processContent(content: string): Promise<void> {
        const parser = await this.parserCreator.createParser(content);
        const note = await parser.prepareNote(content);
        console.log(note);
    }
}
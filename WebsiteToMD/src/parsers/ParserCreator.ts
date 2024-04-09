import { Parser } from './Parser';

export default class ParserCreator {
    private parsers: Parser[];

    constructor(parsers: Parser[]) {
        this.parsers = parsers;
    }

    public async createParser(content: string): Promise<Parser>{
        for (const parser of this.parsers) {
            const testResult = parser.test(content); // Await the test result
            if (testResult) {
                return parser;
            }
        }

    }
}

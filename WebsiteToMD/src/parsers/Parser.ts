import moment from "moment";

export abstract class Parser {
    protected constructor() {}

    abstract test(clipboardContent: string): boolean;

    abstract prepareNote(clipboardContent: string): Promise<string>;

    protected isValidUrl(url: string): boolean {
        try {
            new URL(url);
        } catch (e) {
            return false;
        }
        return true;
    }

    protected getFormattedDateForFilename(): string {
        const date = new Date();
        return moment(date).format('YYYY-MM-DD');
    }

    protected getFormattedDateForContent(): string {
        const date = new Date();
        return moment(date).format('YYYY-MM-DD');
    }
}

const fs = require('fs');
const TurndownService = require('turndown');

const turndownService = new TurndownService();

if (process.argv.length < 3) {
    console.error("Missing HTML filename argument");
    process.exit(1);
}

const htmlFilename = process.argv[2]; 
fs.readFile(htmlFilename, 'utf8', (err, htmlData) => {
    if (err) {
        console.error("Error reading HTML file:", err);
        process.exit(1);
    }

    const markdown = turndownService.turndown(htmlData);
    console.log(markdown); 
});
const WebsiteToMD = require('./main').default; 

const url = process.argv[2]; // Get the URL from the 3rd command-line argument

if (!url) {
  console.error("Please provide a URL as a command-line argument.");
  process.exit(1); 
}

const websiteToMD = new WebsiteToMD(); 
websiteToMD.onload() // Assuming onload initializes necessary components 
  .then(() => {
  const markdownContent = websiteToMD.processContent(url);

    // Output directly to the console (for receiving in Python)
    console.log(markdownContent); 
  })
  .catch(error => console.error("Error processing website:", error));

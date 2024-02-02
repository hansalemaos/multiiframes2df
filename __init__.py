import pandas as pd
from lxml2pandas import subprocess_parsing

JSCODE = r"""
querysel = "*";
function getAllIframes() {
    let allIframes = [];
    let topLevelIframes = document.querySelectorAll('iframe, frame');
    for (let i = 0; i < topLevelIframes.length; i++) {
        console.log(topLevelIframes[i])
        traverseDeeperIntoIframes(topLevelIframes[i])
    }
    function traverseDeeperIntoIframes(ctx) {
        allIframes.push(ctx)
        // Fallback for contentWindow
        const iframeContext = (ctx.contentDocument) ? ctx.contentDocument : ctx.contentWindow.document
        const tmpFrames = iframeContext.querySelectorAll('iframe, frame')
        console.log(iframeContext, tmpFrames)

        for (let i = 0; i < tmpFrames.length; i++) {
            try {
                traverseDeeperIntoIframes(tmpFrames[i])
            } catch (error) {
                console.error(error);
            }
        }
    }
    return allIframes;
}

var newDoc = document.implementation.createHTMLDocument('saved_page');
var newBody = newDoc.body;
try {
    const allIframes = getAllIframes()
    for (var i = 0; i < allIframes.length; i++) {
        var elementsToSave = allIframes[i].contentDocument.querySelectorAll(querysel);
        var clonedElements = Array.from(elementsToSave).map(el => el.cloneNode(true));


        clonedElements.forEach((el, index) => {
            var dummyElement0 = document.createElement('div');
            dummyElement0.innerHTML = `<p>ELEMENTSEPSTART${(index * i) + 1}</p>`;

            newBody.appendChild(dummyElement0.cloneNode(true));
            newBody.appendChild(el);

            var dummyElement = document.createElement('div');
            dummyElement.innerHTML = `<p>ELEMENTSEPEND${(index * i) + 1}</p>`;

            newBody.appendChild(dummyElement.cloneNode(true));
        });




    }
} catch (error) {
    console.error(error);
}


var elementsToSave = document.querySelectorAll(querysel);
var clonedElements = Array.from(elementsToSave).map(el => el.cloneNode(true));
var i = 10000
clonedElements.forEach((el, index) => {
    var dummyElement0 = document.createElement('div');
    dummyElement0.innerHTML = `<p>ELEMENTSEPSTART${(index * i) + 1}</p>`;

    newBody.appendChild(dummyElement0.cloneNode(true));
    newBody.appendChild(el);

    var dummyElement = document.createElement('div');
    dummyElement.innerHTML = `<p>ELEMENTSEPEND${(index * i) + 1}</p>`;

    newBody.appendChild(dummyElement.cloneNode(true));
});

var htmlContent = new XMLSerializer().serializeToString(newDoc);
return htmlContent;

"""


def fast_scrape(
    driver,
    filter_function=None,
    chunks=1,
    processes=4,
    print_stdout=False,
    print_stderr=True,
):
    r"""
    Scrapes data using the provided driver and processes it to return a DataFrame
    which includes each element and its children.

    Args:
        driver: The driver used to scrape the data.
        filter_function: A function to filter the scraped data (default is None).
        chunks: The number of chunks to divide the data into for processing (default is 1).
        processes: The number of processes to use for parallel processing (default is 4).
        print_stdout: Boolean indicating whether to print stdout (default is False).
        print_stderr: Boolean indicating whether to print stderr (default is True).

    Returns:
        pandas DataFrame: The processed and filtered data.

    Example:
        from PrettyColorPrinter import add_printer  # optional
        from seleniumbase import Driver
        from multiiframes2df import fast_scrape

        add_printer(1)
        driver = Driver(uc=True, undetected=True)
        driver.get(r"https://testpages.herokuapp.com/styled/iframes-test.html")
        df = fast_scrape(
            driver=driver,
            filter_function=None,
            chunks=1,
            processes=4,
            print_stdout=False,
            print_stderr=True,
        )
        for name, group in df.groupby("aa_groupnumber"):
            print(name, group)


        df2 = fast_scrape(
            driver=driver,
            filter_function=lambda x: "List" in x and "<html>" not in x and "<body>" not in x,
            chunks=1,
            processes=4,
            print_stdout=False,
            print_stderr=True,
        )
        for name, group in df2.groupby("aa_groupnumber"):
            print(name, group)

    """
    allhtmlcode = ""
    try:
        allhtmlcode = driver.execute_script(JSCODE)
    except Exception as e:
        print(e)
    if not allhtmlcode:
        return pd.DataFrame()
    firstsplit = [
        h.split("</p></div>", maxsplit=1) for h in allhtmlcode.split(r"ELEMENTSEPSTART")
    ]
    firstsplit = [x for x in firstsplit if len(x) == 2]
    secondsplit = [
        [x[0], *x[1].rsplit(f"ELEMENTSEPEND{x[0]}", maxsplit=1)] for x in firstsplit
    ]
    secondsplit = [x[:2] for x in secondsplit if len(x) == 3]
    htmldata = [(x[0], x[1][:-8]) for x in secondsplit if x[1].endswith("<div><p>")]
    if filter_function:
        htmldata = [x for x in htmldata if filter_function(x[1])]
    if not htmldata:
        return pd.DataFrame()
    htmldata = [(str(ini), x[1]) for ini, x in enumerate(htmldata)]
    df = subprocess_parsing(
        htmldata,
        chunks=chunks,
        processes=processes,
        fake_header=False,
        print_stdout=print_stdout,
        print_stderr=print_stderr,
    )
    if df.empty:
        return df
    df["aa_groupnumber"] = df.groupby(
        ["aa_doc_id", "aa_multipart_counter", "aa_multipart"]
    ).ngroup()
    df2 = df.sort_values(by=["aa_doc_id", "aa_groupnumber", "aa_element_id"])
    df2["aa_qty_group"] = (
        df2.groupby("aa_groupnumber")
        .apply(lambda h: h.aa_groupnumber.count())
        .apply(lambda qq: [qq for q in range(qq)])
        .explode()
        .__array__()
    ).astype(int)
    return df2

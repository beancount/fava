# Ideas

- I've been meaning to remove the rendering of all the postings in journals; I think this detail is only needed on-demand, for specific transactions when debugging, akin to getting the "bean-doctor context" or "bean-doctor linked" invoked from Emacs/Vi. For a while I thought I could implement a client-side cursor that would allow one to "expand" a journal row to render its transaction, but that would still require rendering all of them in the HTML output, which is a bit overkill (it's slow for very long journals). Ideally, rendering a transaction's full detail should only be done on-demand. So maybe that's done in a request from a popup or via a link. Not sure how to do it, but the default journal shouldn't have to render all this detail. *(Martin Blais)*

- In the balance renderings, it would be nice to have collapsible trees (I used to have them in a Beancount v1) that when you collapse, the total amount of the subaccounts appear. If you expand, they would disappear and the detail amounts on the subtree items replace them. I've been meaning to add that for a while, just no time for writing FE code. *(Martin Blais)*

- One idea I've been having for a rewrite is to remove the hard-coded views and replace them instead with a FROM expression that would dynamically generate them. This way, all available reports any subset of transactions could be inspected easily. I imagined a textarea from the root page where the user could type an expression that would link to the view page (probably starting a balsheet). There would still be links to commonly used views (e.g. the last few years) but there would be no need to litter that root page with all the possibilities, e.g., for all tags. It's a bit of a mess right now. *(Martin Blais)*

- While I have been shifting my own focus to using the shell more and more in order to support it better, I think it would be awesome to have a tool that provides new reports and visualizations (e.g., a treemap of assets, like this toy experiment I did but better: https://bitbucket.org/blais/beancount/src/9d56d5bfcf9310c3cd9a5fff0df4bf5a915dd911/experiments/treemap/bean-treemap?at=default&fileviewer=file-view-default). *(Martin Blais)*

- Tables of monthly aggregates seem to be a recurring topic. *(Martin Blais)*


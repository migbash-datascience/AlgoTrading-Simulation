Cryptocurrency Data Analysis
---

This project is all about the visualization and quant strategy testing for the cryptocurrency market. It allows you to follow the market as closely as possible in real-time, while giving you full control over incoming financial data.

Getting Started
---
Its very simple to get started. Just clone/download this repository onto your computer.

**How to run?**

System pre-requesits:
 - pipenv,
 - Python version 3+,
 - Have the dependecies installed (outlined below)

*Now, once you got the pre-requisits, run the following in inside the folder*

- ``` pipenv shell ``` to start the virtual enviroment,
- install the dependecies into your **dev** list, from the ```Pipfile.lock``` file, using ```pipenv install --ignore-pipfile --dev```,
- *that is it!*

Dependencies Overview:
---

*This project uses*
- pandas
- numpy
- matplotlib
- binance

All of which can be found in the ```Pipfile.lock``` file.

Algo-Trading Method:
---

This project works in the following way:

**#1.** First, you get the Historical data for a particular period in time from available API Available Exchanges:

- [x] Binance

**#2.** Parse the gathered data into the strategy simulator, for constructing a table (dataframe) with necessary details, to be used for further analysis.

**#3.**  Pass the strategy specific table (dataframe), into the risk_management() method, to calculate the necessary risk assessment for the respective strategy table (dataframe).

**#4.** After the strategy has been risk analysed thoroughly, the metrics + the strategy ID are saved/appended to a list of risk_metrics which can then be saved into a target file.

**#5.** The strategy ```signals``` are saved into a JSON file for future further analysis.


Current Testing Methods
---

- [x] x2 SMA Cross
- [ ] x2 EMA Cross

Project Structure
---

```hist_data/``` -> contains a snapshot of historical data in JSON format from a target exchange for a particular trading market pair/ticker.

```instance/``` -> contains local files that are to be filled out and used on a local machine, such as: secret keys, api keys, etc.

```other/``` -> contains random code used thorughout the project that may or may not be useful in the future.

```results/``` -> contains the strategy processed output data in JSON format from ```strategy/```, genereated from any target ```hist_data/``` JSON file.

```strategy/``` -> contains all target and/or experimental strategies used in the project, for testing and validation.

```out.json``` -> contains the strategy processed output data in JSON format from ```strategy/```, genereated from any target ```hist_data/``` JSON file.

```main.py``` -> contains all of the main logic to orchistrate the project from one single file, with stuff like: variables, __main__, etc.

```MarektOnClosePortfolio.py``` -> contains the backtesting for a strategy dataframe (df) for tracing and tracking the performance of the stratey using real trading values and variables.

Procedural Examples:
---

This is a flow diagram with represntaition of how the poroject flows and works:
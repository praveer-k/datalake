Welcome to Datalake docs!
=================================

Hopefully you reached this documentation using the following the command:

.. code-block:: bash
   
   cd datalake
   poetry shell
   poetry install
   poetry run docs --serve

Quick overview:

.. toctree::
   :maxdepth: 3

   pages/directory_structure
   pages/architecture

The project has a few dependencies:

- |minio_image| |minio_local_link|
   Minio is object storage used as a datalake to store large amounts of data.
- |postgres_image| |postgres_local_link|
   Postgres is the database used in this project to display data on the dashboard.
- |spark_image| |spark_local_link|
   Spark is is used for cleaning, aggregating and loading data. It is a analytics tool that can scale processing of data using a distributed environment.


These dependencies are installed in an isolated environment using docker compose. 
But, before running the docker compose, it is required that you download the raw files from the Yelp Dataset and store it in the the same directory at ./.local/downloads/yelp_dataset.tar

You can achive this by just running the following command:

.. code-block:: bash
   
   poetry run download

The command above utilizes .env file stored in this directory. It contains log, doc, storage, database, yelp_dataset settings. Here is a sample file:

.. code-block:: bash

   LOG_LEVEL=debug

   DOCS__TITLE="NewYorker.com"
   DOCS__DESCRIPTION="Data Engineering Programming Challenge"
   DOCS__VERSION="0.1.0"
   DOCS__SOURCE_DIR="datalake/docs"
   DOCS__BUILD_DIR="build/docs"
   DOCS__CACHE_DIR=".local/dependency"
   DOCS__PLANTUML_JAR="https://github.com/plantuml/.../plantuml-asl-1.2024.0.jar"

   STORAGE__USER=minio_user
   STORAGE__PASSWORD=minio_password
   STORAGE__ENDPOINT=http://minio:9000
   STORAGE__DATA_LAKE_BUCKET=datalake

   DB__HOST=localhost
   DB__PORT=5432
   DB__USER=root
   DB__EMAIL=praveerkumar17@gmail.com
   DB__PASSWORD=example
   DB__NAME=yelp_dataset

   YELP_DATASET__AUTH__NAME="Praveer Kumar"
   YELP_DATASET__AUTH__EMAIL="praveerkumar17@gmail.com"
   YELP_DATASET__AUTH__SIGNATURE="praveerk"
   YELP_DATASET__DOWNLOAD_LINK="https://www.yelp.com/dataset/download"
   YELP_DATASET__LOCAL_PATH=".local/downloads/yelp_dataset/"

.. Note::

   The downloaded files are stored in the specific place so that docker compose can pick that path and push that data to the datalake.

Now, you can run the docker compose up command to start the dependent instances of minio, postgres and spark.

.. code-block:: bash
      
   docker compose up -d

Minio utilizes the downloaded data and uploads it to the datalake/raw directory on the object store and,
Postgres instance creates a database called yelp_dataset.

This allows us to have a pre-configured environment to run spark pipelines. Now we can clean, aggregate and load data from raw files and, eventually, visualize it on a dashboard.

The configured environment however still does not contain the files or package required to run the datalake module.
This needs to be installed before submiting the task to spark master instance.

To install the package run the following command:

.. code-block:: bash
      
   poetry build
   docker exec -it spark-master pip install ./dist/datalake-0.1.0.tar.gz

Running poetry build creates a wheel file that can be utilized by the docker container to run the pipeline. Since, the volume is already mounted so all we need to do is install the package as is done by the above command.
Once this is done, we can run the pipeline as follows:

.. code-block:: bash

   docker exec -it spark-master python -m datalake --name yelp --option clean
   docker exec -it spark-master python -m datalake --name yelp --option aggregate
   docker exec -it spark-master python -m datalake --name yelp --option load

Now, we can run the dashboard and fiddle with the loaded data.

.. code-block:: bash

   poetry run dashboard

That's it !

.. |minio_image| image:: _static/minio.svg 
   :height: 1.2em
   :width: 1.2em

.. |postgres_image| image:: _static/postgres.svg 
   :height: 1.2em
   :width: 1.2em

.. |spark_image| image:: _static/spark.svg
   :height: 1.2em
   :width: 1.2em

.. |streamlit_image| image:: _static/streamlit.svg
   :height: 1.2em
   :width: 1.2em

.. |minio_local_link| raw:: html

   <a href="http://localhost:9000" target="_blank">Minio Instance</a>

.. |postgres_local_link| raw:: html

   <a href="http://localhost:5000" target="_blank">Postgres Instance</a>

.. |spark_local_link| raw:: html
   
   <a href="http://localhost:8080" target="_blank">Spark Instance</a>

.. |streamlit_local_link| raw:: html
   
   <a href="http://localhost:8501/docs" target="_blank">Streamlit Instance</a>



# Data Engineering Programming Challenge

To run the project you need following dependencies installed on your system.

- Python >=3.11.9
- Poetry
- Docker
- Java (to run docs - plantuml files)

After installing all the dependecies, copy the repository to a desired place in the filesystem and run the following command to see documentation:

```bash
    cd datalake
    poetry shell
    poetry install
    poetry run docs --serve
```

On windows, an extra package needs to be installed

```bash
poetry install --extras postgres
```

You will now have acces to the overall architecture and project structure using this documentation.
visit this link to see [documentation link](http://localhost:8000)

Here is a brief list of useful commands with project sturcture.

**Project Structure:**

```text
   datalake
   ├── src
   │   ├── config
   │   ├── dashboard
   │   ├── docs
   │   ├── downloaders
   │   ├── pipelines
   │   └── __main__.py
   ├── .env
   ├── ...
   ├── docker-compose.yaml
   ├── Dockerfile
   ├── pyproject.toml
   └── README.md
```

Here is the sample **.env** file with required settings.

```bash
   LOG_LEVEL=debug

   DOCS__TITLE="AmazingCompany.com"
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

   YELP_DATASET__AUTH__NAME="Xxxxx Xxxxx"
   YELP_DATASET__AUTH__EMAIL="xxxxxxxxx@gmail.com"
   YELP_DATASET__AUTH__SIGNATURE="xxxxxx"
   YELP_DATASET__DOWNLOAD_LINK="https://www.yelp.com/dataset/download"
   YELP_DATASET__LOCAL_PATH=".local/downloads/yelp_dataset/"
```

After installing all the packages, run poetry download to download the dataset.

```bash
   poetry run download
```

After download finishes following should be visible in your local folder.

```text
   datalake
   ├── .local
   │   ├── downloads
   │   │   ├── Dataset_User_Agreement.pdf
   │   │   ├── yelp_academic_dataset_business.json
   │   │   ├── yelp_academic_dataset_checkin.json
   │   │   ├── yelp_academic_dataset_review.json
   │   │   ├── yelp_academic_dataset_tip.json
   │   │   └── yelp_academic_dataset_user.json
   │   ├── ...
   │   └── yelp_dataset.tar
   └── ...
```

This, data will be used by docker compose `minio` to load data to the `datalake`. Once, the data is there you can run the pipeline using following commands.

```bash
   docker compose up -d
   poetry build
   docker exec -it spark-master pip install ./dist/datalake-0.1.0.tar.gz
   docker exec -it spark-master python -m datalake --name yelp --option clean
   docker exec -it spark-master python -m datalake --name yelp --option aggregate
   docker exec -it spark-master python -m datalake --name yelp --option load
```

In case docker compose throws error while initiallizing postgres instance for the first time then just run it again to continue.

**Note:-** That the load command is optional and is added merely to make is easier for the end user to see the transformed data at a glance. To visualise, I have used streamlit. You can see the results on the dashboard by running the following command.

```bash
   poetry run dashboard
```

**Please note:-** The selection of `business name` on the dashboard takes sometime to fetch data as sql queries are slow and is not cached. To avoid delay in ploting graphs, all the aggregated data are pre-fetched. It may take a while before dashboard is useable. In my testing it took 3-4 mins !!!

Dashboard uses both database and storage to show data so, last command `docker exec -it spark-master python -m datalake --name yelp --option load` is important to run before running the dashboard.

That's it !

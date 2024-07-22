Directory structure
===========================
Following is the structure of the code base

.. code-block::

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


`config` directory contains logging and other settings of the project and is utilised by all the 4 entrypoints of the package.
`pipelines`, `docs`, `download`, `dashboard`

`pipelines` is a special case that needs to be packaged as a module and rest of the application does not need the same treatment.

Therefore, the packaged application has entrypoints only for pipelines.


Three possible options here are:

.. code-block::

    python -m datalake --name yelp --option clean
    python -m datalake --name yelp --option aggregate
    python -m datalake --name yelp --option load

Rest of the package can be invoked using poetry run commands:

.. code-block::

    poetry run docs --serve
    poetry run dashboard
    poetry run download


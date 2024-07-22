Architecture
===========================

Following uml diagram shows the communication between all the actors involved in running the process.

.. uml:: ../_diagrams/sequence.puml
    :alt: Diagram to show various actors invovled and there interactions
    :align: center
    :height: 30em

So, in essence, the user triggers various functions by sending the command to the pipeline to clean and aggregate data.
Pipeline in turn reads that data from the storage bucket and stores it back to another part of the bucket. The final data gets stored into the database.
This data can now be used by the dashboard to show stats.
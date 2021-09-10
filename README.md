__Battery Lifecycle (BLC) Framework__

The Battery Lifecycle (BLC) Framework is an open-source platform that provides tools to visualize, analyze, and share battery data through the technology development cycle, including data from material characterization, cell testing, manufacturing, and field testing. The BLC framework provides users with a unified view of their data that they can use to optimize materials and cell configurations, validate cell performance under application conditions, and mitigate manufacturing variations and field failures. BLC has four components: data importers, one or more databases, a front-end for querying the data and creating visualizations, and an application programming interface to process the data. BLC supports multiple users with different access permissions. Instead of building the system from the ground up, we developed BLC around Redash, a robust open-source extract-transform-load engine. BLC has been deployed for two applications: (i) tracking the development of a single battery technology from the lab to a manufacturing line and systems installed in the field, and (ii) comparing studies of multiple cells of the same battery chemistry and configuration. The latter implementation is publicly available at www.BatteryArchive.org. 

The code and documentation in this repository can be used to build and operate a site like batteryarchive.org.

The detailed installation steps are included in the [blc_Installation_steps.pdf](blc_Installation_steps.pdf) file in the repository.

To learn more about the design of the software, read our paper available online at https://ecsarxiv.org/h7c24/

For more information, contact us at info@batteryarchive.org.

#
Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.


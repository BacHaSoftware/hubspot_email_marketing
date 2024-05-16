
<a name="readme-top"></a>

<!-- PROJECT DETAILS -->
<br />
<div align="center">
  <a href="https://github.com/BacHaSoftware/hubspot_email_marketing">
    <img src="/bhs_integration_hubspot/static/description/icon.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Hubspot Integration</h3>

  <p align="center">
    A product of Bac Ha Software allows to Synchronized data between Hubspot and Odoo, provides comprehensive solutions to email marketing and related problems.
</p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact-us">Contact us</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<div align="left">
  <a href="https://github.com/BacHaSoftware/hubspot_email_marketing">
    <img src="/bhs_integration_hubspot/static/description/banner.gif" alt="Setting">
  </a>
</div>


#### Key Features:

🌟 <code>Hubspot Contact And Companies</code>: Synchronize contact and company data between Hubspot and Odoo daily. Synchronized data includes: name, city, state, country, industry...

🌟 <code>Add To Blacklist</code>: Automatically add to email blacklist Suppressed emails on SES and delete their mailing contacts.

🌟 <code>Update Unqualified Contacts On Hubspot</code>: Automatically update contacts on hubspot to UNQUALIFIED when they are blacklist on Odoo (run schedule action once a day, after retrieve BOUNCE and COMPLAIN emails from SES and add to mail blacklist).

🌟 <code>Mailing Contact Features</code>: Block duplicate mailing contacts, import mailing contact data into mailing list, add to blacklist feature.

🌟 <code>Blacklist Domain</code>: Add model to record blacklist domains. Block import emails belonging to blacklist domains (edu,gov,org,....).

🌟 <code>Add And Remove From Old List</code>: Add mailing contacts to a list and delete them from their old lists.

🌟 <code>Mailing Contact Contacted</code>: Record mailing contacts that no longer want to change their mailing list (example: current customers). The last purpose is to no longer send marketing emails to these mailing contacts.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

<!-- PREREQUISTES  -->
### Prerequisites

This module needs the Python library <code>slackclient</code>, <code>html-slacker</code>, otherwise it cannot be installed and used. Install them through the command
  ```sh
  sudo pip3 install simplejson
  sudo pip3 install hubspot
  sudo pip3 install hubspot-api-client
  sudo pip3 install boto3
  ```
And this module also depends on our other module: Mass Mailing _(bhs_mass_maling)_
### Installation

1. Install module  <code>bhs_integration_hubspot</code>
2. Config System Parameters connect AWS SES: <code>ses_user_access_key</code>, <code>ses_user_secret_key</code>, <code>ses_region</code>
3. Config Blacklist Domain
4. Config time run cron sync data

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

A product of Bac Ha Software allows to Synchronize data between Hubspot and Odoo, provides comprehensive solutions to email marketing and related problems.

#### Featured Highlight:

🌟 <code>Data Synchronization</code>: Hubspot data and odoo mailing contacts are synchronized daily.

🌟 <code>Simple Setup</code>: After install module, just need to input HubSpot API Key at General Settings.



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT US-->
## Contact us
Need assistance with setup or have any concerns? Contact Bac Ha Software directly for prompt and dedicated support:
<div align="left">
  <a href="https://github.com/BacHaSoftware">
    <img src="/bhs_integration_hubspot/static/description/imgs/logo.png" alt="Logo" height="80">
  </a>
</div>

📨 odoo@bachasoftware.com

🌍 [https://bachasoftware.com](https://bachasoftware.com)

[![WEBSITE][website-shield]][website-url] [![LinkedIn][linkedin-shield]][linkedin-url]

Project Link: [https://github.com/BacHaSoftware/hubspot_email_marketing](https://github.com/BacHaSoftware/hubspot_email_marketing)


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[license-url]: https://github.com/BacHaSoftware/hubspot_email_marketing/blob/17.0/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/bac-ha-software
[website-shield]: https://img.shields.io/badge/-website-black.svg?style=for-the-badge&logo=website&colorB=555
[website-url]: https://bachasoftware.com
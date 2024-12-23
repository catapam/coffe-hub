# Coffeehub

<a href="https://coffee-hub-64aa59561310.herokuapp.com/" target="_blank">Live project can be viewed here</a>

Welcome to Coffee Hub, your one-stop platform for premium coffee and related merchandise. This e-commerce application showcases advanced functionalities, delivering a seamless and enjoyable shopping experience.

![amiresponsive screenshot](documentation/responsive.png)

<div align="center">

![](https://tokei.rs/b1/github/catapam/coffe-hub?category=files)
![](https://tokei.rs/b1/github/catapam/coffe-hub?category=code)
![](https://tokei.rs/b1/github/catapam/coffe-hub?category=comments)

</div>

# Table of Contents



# Introduction

Coffee Hub is a luxurious e-commerce platform dedicated to coffee enthusiasts, offering a curated selection of premium coffee beans, brewing equipment, and accessories. The platform is designed to provide a seamless shopping experience, integrating a robust payment gateway, real-time inventory updates, and personalized recommendations based on user preferences. Coffee Hub is the perfect destination for anyone looking to elevate their coffee experience.

## Objective

## Audience

## Solution

## Scope

# Business and Marketing plan

## User Experience

Coffee Hub is meticulously crafted to deliver an elegant and intuitive user experience. The platform features a sleek dark-mode design with warm, rich colors that reflect the essence of coffee culture. Navigation is effortless, with clear categorization of products, a search functionality, and an easy checkout process. Users can create accounts to save preferences, track orders, and manage their profiles. Accessibility and responsiveness are prioritized, ensuring that Coffee Hub looks and performs beautifully across all devices.

## Market

## Revenue model

## Marketing

## KPIs

## Risks

# Agile Methodology and Planning

## Epics

### Epic 1: Project Setup and Initial Configuration

In this epic, the primary objective is to fully establish the Django front-end website, with comprehensive content management through the admin dashboard. Key deliverables include the creation of branding elements and the development of a functional, polished landing page that reflects the final version of the site. Additionally, this epic covers the initial setup, including the installation of essential Python modules and the configuration of testing parameters to ensure the front-end website operates smoothly.

<details><summary><b>User Stories</b></summary>

- [STORY 1.1 - As a developer, I want to set up the Django environment and establish the initial project structure so that the project has a solid foundation for further development.](https://github.com/catapam/coffe-hub/issues/7)
- [STORY 1.2 - As a developer, I want to select and configure a SQL database (MySQL or PostgreSQL) so that the project has a reliable and scalable data storage solution.](https://github.com/catapam/coffe-hub/issues/8)
- [STORY 1.3 - As a developer, I want to deploy the Django project to Heroku so that the application is accessible online and ready for further development.](https://github.com/catapam/coffe-hub/issues/9)
- [STORY 1.4 - As a developer, I want to create and integrate basic front-end templates so that the application has a consistent design and user experience.](https://github.com/catapam/coffe-hub/issues/10)
- [STORY 1.5 - As a developer, I want to establish copyright, branding, and basic project documentation so that the project is legally compliant and easy to understand.](https://github.com/catapam/coffe-hub/issues/11)
- [STORY 1.6 - As a developer, I want to implement automated testing using Python so that the project's codebase remains stable and errors are caught early in development.](https://github.com/catapam/coffe-hub/issues/12)

</details>

### Epic 2: User Authentication and Authorization

This epic focuses on implementing a robust user authentication and authorization system. The goal is to enable secure user registration, login, and access management. Core tasks include integrating Django’s authentication framework, setting up user roles and permissions, and ensuring data security through encryption. By the end of this epic, the website will support secure user interactions, with role-based access control fully implemented.

<details><summary><b>User Stories</b></summary>

- [STORY 2.1 - As a user, I want to register an account so that I can access the system.](https://github.com/catapam/coffe-hub/issues/13)
- [STORY 2.2 - As a user, I want to log in to my account so that I can access my portfolio.](https://github.com/catapam/coffe-hub/issues/14)
- [STORY 2.3 - As a user, I want to reset my password if I forget it so that I can regain access to my account.](https://github.com/catapam/coffe-hub/issues/15)
- [STORY 2.4 - As an admin, I want to assign roles to users so that I can control access to different functionalities.](https://github.com/catapam/coffe-hub/issues/16)

</details>

### Epic 3: Store

This epic is dedicated to implementing the product catalog, search, and detailed views for items in the store. It ensures users can browse, filter, and find products with ease. Key features include a responsive product display, search functionality, and categorization to enhance the shopping experience.

<details><summary><b>User Stories</b></summary>

- [STORY 3.1 - As a customer, I want to browse a catalog of products with filtering options so that I can easily find products based on my preferences.](https://github.com/catapam/coffe-hub/issues/17)
- [STORY 3.2 - As a customer, I want to search for products by name or keywords so that I can quickly find what I’m looking for.](https://github.com/catapam/coffe-hub/issues/18)
- [STORY 3.3 - As a customer, I want to view detailed information about a product so that I can make an informed purchasing decision.](https://github.com/catapam/coffe-hub/issues/19)
- [STORY 3.4 - As an admin, I want to categorize products so that customers can easily browse by product type.](https://github.com/catapam/coffe-hub/issues/20)
- [STORY 3.5 - As an admin, I want to manage product inventory levels so that customers can see product availability before making a purchase.](https://github.com/catapam/coffe-hub/issues/21)
- [STORY 3.6 - As a customer, I want to leave reviews and ratings for products so that I can share my experience and help others decide.](https://github.com/catapam/coffe-hub/issues/22)
- [STORY 3.7 - As a customer, I want to add, remove, and edit products in my cart, so I can easily manage my shopping list before checkout.](https://github.com/catapam/coffe-hub/issues/229)

</details>

### Epic 4: Payment Gateway

This epic focuses on integrating a secure and efficient payment system into the website. Key deliverables include the implementation of Stripe for payment processing, a user-friendly checkout process, and comprehensive payment feedback. By the end of this epic, users will be able to complete transactions smoothly, with secure data handling and clear notifications.

<details><summary><b>User Stories</b></summary>

- [STORY 4.1 - As a developer, I want to integrate the Stripe payment gateway so that users can make secure payments for their purchases.](https://github.com/catapam/coffe-hub/issues/23)
- [STORY 4.2 - As a user, I want to go through a structured checkout process so that I can complete my purchases smoothly.](https://github.com/catapam/coffe-hub/issues/24)
- [STORY 4.3 - As a user, I want to receive feedback after making a payment so that I know if my purchase was successful or if there was an issue.](https://github.com/catapam/coffe-hub/issues/25)
- [STORY 4.4 - As a developer, I want to log transaction details so that users can access their payment history and admins can track order details.](https://github.com/catapam/coffe-hub/issues/26)
- [STORY 4.5 - As a developer, I want to validate orders before processing payment so that I can ensure correct pricing and inventory levels.](https://github.com/catapam/coffe-hub/issues/27)
- [STORY 4.6 - As an admin, I want to manage refunds and payment reversals so that customers can be refunded for eligible purchases.](https://github.com/catapam/coffe-hub/issues/28)

</details>

### Epic 5: Account Management

This epic focuses on creating a comprehensive user account management system. Key functionalities include managing user profiles, changing passwords, viewing order history, and managing addresses. Additionally, account deactivation and reactivation processes will be implemented, ensuring users have full control over their accounts.

<details><summary><b>User Stories</b></summary>

- [STORY 5.1 - As a user, I want to be able to view and update my profile information so that my account details are accurate and up to date.](https://github.com/catapam/coffe-hub/issues/29)
- [STORY 5.2 - As a user, I want to be able to change my password securely so that my account remains protected.](https://github.com/catapam/coffe-hub/issues/30)
- [STORY 5.3 - As a user, I want to view my order history so that I can keep track of past purchases and their details.](https://github.com/catapam/coffe-hub/issues/31)
- [STORY 5.4 - As a user, I want to manage multiple shipping addresses so that I can select the correct one during checkout.](https://github.com/catapam/coffe-hub/issues/32)
- [STORY 5.5 - As a user, I want the option to deactivate my account so that I can manage my privacy and control my account’s availability.](https://github.com/catapam/coffe-hub/issues/33)

</details>

### Epic 6: SEO and Marketing

This epic aims to optimize the platform for search engines and enhance its online presence through marketing strategies. The focus includes implementing SEO best practices, integrating social sharing features, and setting up analytics to track user behavior. These efforts ensure the site is discoverable and aligned with marketing goals.

<details><summary><b>User Stories</b></summary>

- [STORY 6.1 - As a developer, I want to create SEO-friendly URLs and page titles so that the site ranks better in search engine results.](https://github.com/catapam/coffe-hub/issues/34)
- [STORY 6.2 - As a developer, I want to add meta descriptions and keywords to key pages so that search engines better understand the content.](https://github.com/catapam/coffe-hub/issues/35)
- [STORY 6.3 - As a developer, I want to create a sitemap.xml file so that search engines can crawl the site more effectively.](https://github.com/catapam/coffe-hub/issues/36)
- [STORY 6.4 - As a developer, I want to add a robots.txt file to control which parts of the site search engines can crawl, so that unwanted content is not indexed.](https://github.com/catapam/coffe-hub/issues/37)
- [STORY 6.5 - As a user, I want to easily share content from the site on social media so that I can spread awareness of the products and engage with others.](https://github.com/catapam/coffe-hub/issues/38)
- [STORY 6.6 - As a site owner, I want to monitor site traffic with Google Analytics so that I can understand user behavior and improve the site based on data insights.](https://github.com/catapam/coffe-hub/issues/39)
- [STORY 6.7 - As a site owner, I want to integrate a newsletter signup form so that I can build a mailing list and engage users with updates and promotions.](https://github.com/catapam/coffe-hub/issues/221)

</details>

## MoSCoW Methodology

All the six epics and their stories are essential for the project delivery, providing all necessary features and expected standards. Therefore, most of these tasks are classified as 'Must Have' or 'Should Have.'

User stories are broken down into tasks, where each task is categorized as 'Must Have,' 'Should Have,' 'Could Have,' or 'Won’t Have.' Each task is also assigned a story point weight of 1, 2, or 4, reflecting the effort required to complete it.

The story point weight and MoSCoW priority of each task for the three sprints (Epics 1, 2, and 3) were carefully planned to allow flexibility in execution. 'Must Haves' do not exceed 60% of the sprint's total story points. 

For documenting and visualization, the sprints were closed with undone tasks/stories, those are all non-'Must have' and would be moved to a future sprint. They were all place in backlog for now but kept inside the sprint for documentation purposes. 

The details for each sprint are provided below:

### Sprint/Epic 1

**Story Point / MoSCoW** | **Must Have** | **Should Have** | **Could Have**
:-----:|:-----:|:-----:|:-----:
**1** | 10 | 0 | 0 |
**2** | 10 | 4 | 0 |
**4** | 1 | 2 | 3 |
**Total** | 34 | 16 | 12 |

- Total story points: 62
- Total 'Must Have': 34
- Must Have proportion: 54.83%

### Sprint/Epic 2

**Story Point / MoSCoW** | **Must Have** | **Should Have** | **Could Have**
:-----:|:-----:|:-----:|:-----:
**1** | 4 | 3 | 0 |
**2** | 8 | 5 | 10 |
**4** | 0 | 0 | 5 |
**Total** | 20 | 13 | 40 |

- Total story points: 73
- Total 'Must Have': 20
- Must Have proportion: 27.40%

### Sprint/Epic 3

**Story Point / MoSCoW** | **Must Have** | **Should Have** | **Could Have**
:-----:|:-----:|:-----:|:-----:
**1** | 0 | 0 | 4 |
**2** | 10 | 5 | 4 |
**4** | 10 | 3 | 3 |
**Total** | 60 | 22 | 24 |

- Total story points: 106
- Total 'Must Have': 60
- Must Have proportion: 56.60%

### Sprint/Epic 4

**Story Point / MoSCoW** | **Must Have** | **Should Have** | **Could Have**
:-----:|:-----:|:-----:|:-----:
**1** | 0 | 2 | 3 |
**2** | 0 | 10 | 1 |
**4** | 12 | 2 | 0 |
**Total** | 48 | 30 | 5 |

- Total story points: 83
- Total 'Must Have': 48
- Must Have proportion: 57.83%

### Sprint/Epic 5

**Story Point / MoSCoW** | **Must Have** | **Should Have** | **Could Have**
:-----:|:-----:|:-----:|:-----:
**1** | 0 | 0 | 5 |
**2** | 2 | 7 | 1 |
**4** | 8 | 2 | 0 |
**Total** | 36 | 22 | 7 |

- Total story points: 65
- Total 'Must Have': 36
- Must Have proportion: 55.38%

### Sprint/Epic 6

**Story Point / MoSCoW** | **Must Have** | **Should Have** | **Could Have**
:-----:|:-----:|:-----:|:-----:
**1** | 0 | 0 | 7 |
**2** | 1 | 14 | 0 |
**4** | 12 | 0 | 1 |
**Total** | 50 | 28 | 11 |

- Total story points: 89
- Total 'Must Have': 50
- Must Have proportion: 56.18%

## Sprint Length

Based on the total story points, each sprint was assigned 1 week lenght.

## Reviews

Tasks and tickets were reviewed every 3 work days. New tickets, such as bug reports, may have been incorporated into the planning, which sometimes resulted in the removal of tasks from sprints or adjustments to their MoSCoW priorities.

# Data structure

* Data structure was created using <a href="https://drawsql.app/" target="_blank">drawSQL</a>:

# Design

Coffee Hub's design combines elegance with functionality, offering users a visually striking yet highly intuitive experience. The platform leverages a luxurious dark-mode theme with warm, coffee-inspired hues, accented by gold and white details, to create a sophisticated ambiance. This design reflects the essence of premium coffee culture while ensuring usability and accessibility.

Key design principles include:

* **User-Centric Design**: The platform is crafted to provide a seamless user experience, with intuitive navigation, clear categorization of products, and a streamlined checkout process.
* **Responsive Design**: Coffee Hub is fully responsive, delivering a consistent and polished experience across all devices, whether desktop, tablet, or mobile.
* **Visual Elegance**: Rich gradients, subtle lighting effects, and high-quality imagery highlight the premium nature of the products.
* **Accessibility**: The design adheres to accessibility standards, ensuring all users can navigate and interact with the platform effortlessly.
* **Security**: Robust security measures, including secure authentication and encrypted transactions, are integrated to protect user data and payment information.

## Color scheme

* Used <a href="https://coolors.co/" target="_blank">Coolors</a> to create the palette:

![coolors screenshot](documentation/palette.png)

## Typography

* The fonts were choosen on <a href="https://fonts.google.com/" target="_blank">Google fonts</a>, thinking of keeping the same sentiment as the colors passed.
* Primary font family for body text: **Nunito**
* Font family for headings: **Lato**

## Wireframes

* Wireframes were created in Canva during the branding and theme planning, it can be checked here:

<details><summary><b>Mobile</b></summary>
</details>
<details><summary><b>Desktop</b></summary>
</details>

# Features

## Existing Features

## Future Features

# How to Use

## Store

## User Portal

## Staff Access

## Admin access

# Technology Used

## Languages

* Python
* Django
* Sql
* HTML
* CSS
* JavaScript

## Frameworks, Libraries, and Tools

* **Django**: The main web framework used for building the application.
* **PostgreSQL**: The relational database used to store user and portfolio data.
* **Bootstrap**: For responsive design and styling.
* **AllAuth**: For user authentication
* **Crispy Forms**: For all forms
* **Django Countries**: List of countries and abreviations for Stripe compatibility
* **Chart.js**: For data visualizations in the performance dashboard.
* **Heroku**: For application deployment.
* **Git**: For version control.
* **Payment Integration**: Stripe
* **Email Marketing**: Mailchimp API
* **Cloudinary**: Dynamic assets hosting (images)
* **Canva.com**: Branding and logo
* **Favicon.io**: For manifest and favicon creation
* **freeprivacypolicy.com**: Privacy privacy generator

# Deployment

To deploy the application on Heroku:

1. Visit the Heroku website, log in, or create a new account.
2. On the dashboard, click "New" and select "Create new app."
3. Enter a unique app name and choose a region.
4. Click "Create app."
5. Navigate to the "Settings" tab and find "Config Vars."
6. Click "Reveal Config Vars," add "PORT" as a key with the value "8000," and click "Add."
7. Add other vars like DISABLE_COLLECTSTATIC and SECRET_KEY
8. For the database, email, cloud images hosting and payment gateway setups, add the relevant variables to the heroku app too, example: DATABASE_URL, EMAIL_HOST_PASSWORD, EMAIL_HOST_USER, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_CLOUD_NAME, STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY, STRIPE_WH_SECRET ...
9. Scroll down to the "Buildpacks" section, click "Add buildpack," and select "Python."
10. Repeat step 7 to add "Node.js," ensuring "Python" is listed first.
11. Scroll to the top and select the "Deploy" tab.
12. Choose GitHub as the deployment method, then search for your repository and click "Connect."
13. Scroll down and either "Enable Automatic Deploys" to update the code each time it is pushed to GitHub, or choose "Manual Deploy" for manual updates.

# Testing

- Testing was mainly made using Google Chrome Developer Tools, including the mobile and responsive views.
- Lighthouse tab of developer tools was used to score the site regarding Performance, Acessibility and SEO.
- The site was tested on other devices using Edge, Firefox and Safari. When testing on desktops with OS: Mac iOS and Windows 11. And on mobile OS: Android. More mobile tests were made using the inspector tools on desktop device.
- The apps Operations, Metrics and Contacts are not being tested at this point as they are just place holders at this point in time.

## HTML, accessibility and performance

| **Page** | **<a href="https://validator.w3.org/nu/#textarea" target="_blank">W3C Markup validator</a>** | **<a href="https://wave.webaim.org/" target="_blank">Wave accessibility</a>** | **Performance** | **Acessibility** | **Best practices** | **SEO** |
|------------------------------------------|------------|------------|------------|------------|------------|------------|


* Passed state means the test was run, and returned no errors or alerts
* Due to the nature of dashboard pages, Wave was run using the browser extension rather than the site tool.
* M=mobile, D=desktop.
* Performance issues caused by initial server response (TTFB) were ignored due to the server were the current site is hosted being a free version of a third party service I don't have much control over. Initial server response may also be result of slow postgress queries, which is not the focus for this project, those can be dealt with once the site is deployed to a permanent server
* Render blocking issues were avoided whenever possible, and only left when optimizing caused major layout shifts.

## CSS
| **File** | **<a href="https://jigsaw.w3.org/css-validator/" target="_blank">WC3 CSS validator</a>** |
|----------|----------------------------|


## Java Script
| **File** | **<a href="https://jshint.com/" target="_blank">JS hint ES6</a>** |
|----------|----------------------------|


## Python
| **File** | **<a href="https://pep8ci.herokuapp.com/" target="_blank">PEP8 validator</a>** |
|----------|-------------------------|


## Manual testing

## Bugs

# Credits

## Code

Two youtube videos were of grand relevance as guidance for coding:
* <a href="https://www.youtube.com/watch?v=sBjbty691eI&list=PLXuTq6OsqZjbCSfiLNb2f1FOs8viArjWy" target="_blank">Initial setup and general settings</a> 
* <a href="https://www.youtube.com/watch?v=WbNNESIxJnY&t=9796s" target="_blank">Saas specifics and more advanced development</a> 
* <a href="https://github.com/Code-Institute-Solutions/boutique_ado_v1" target="_blank">Code institute Boutique Ado ecomm project</a> - Used as guidance for essential core ecomm functionalities
* <a href="https://github.com/catapam/investnest" target="_blank"> InvestNest</a> - Re-usage of dashboard and account management functionalities (project of my own)

## Content

* ChatGPT and Claude AI: For text reviews, home page images, troubleshooting errors and copywriting assistance.

## Documentation

* <a href="https://github.com/kpetrauskas92/Mont-Adventures-PP5" target="_blank"> Mont Adventures</a> - Inspiration for README sessions and structure

# Acknowledgements

* Gareth Mc Girr: My mentor, for all the help and advice throughout the project.
* Code Institute: For all the training and guidance.
* WP Engine: My current employer, for providing all the support necessary and allowing great networking.
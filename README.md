# 📰 Newspaper Daily Archiver

This project automates the **daily archiving of newspaper articles** using [Archive.org](https://archive.org/), with a primary focus on Bangladeshi newspapers for now. It extracts all articles from the homepage of selected newspapers each day and submits them for permanent storage. The output is a CSV log containing original article URLs, archive URLs, and success status — useful for researchers, journalists, and digital preservationists.

---

## ✅ Features

* 📜 Archives multiple newspapers (configurable in `newspapers.txt`)
* 🧠 Extracts only **articles published today**
* 🌐 Filters out external, social, or non-article links
* 🗂 Saves results into a CSV (`all_articles_YYYY-MM-DD.csv`)
* ⚙️ Ready for daily automation with **GitHub Actions** or `cron`
* 🌐 Uses **Selenium** to load dynamic pages, handling JavaScript-rendered content

---

## ⚠️ Known Limitations & Drawbacks

* 🛡️ Some newspapers employ **Cloudflare or other bot protections** that require human interaction (CAPTCHA, waiting periods), which this tool cannot bypass automatically.
* 🕒 When security checks occur, you might experience long waits or failed fetches.
* 📦 Archive.today submissions may **fail silently** or intermittently due to service limitations or rate-limiting.
* 🔄 The tool **only submits URLs** to Archive.today without verifying if archiving succeeded.
* ⚠️ Use responsibly: excessive automated submissions may lead to temporary IP blocks or throttling by archive.today or target websites.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/md-k-sarker/news-archiver.git
cd news-archiver
```

---

### 2. Add Newspaper URLs

Edit the file `newspapers.txt` and include the homepage URLs of the newspapers you'd like to archive. Example:

```
https://www.prothom-alo.com
https://www.banglanews24.com
https://www.ittefaq.com.bd
```

---

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the Script

```bash
python code/news_archiver.py
```

* This will create a CSV file like `all_articles_2025-07-10.csv` containing:

  * Original article URL
  * Time the archive request was made

---

## 🔁 Daily Automation

This repo includes a GitHub Actions workflow to automate the process:

* File: `.github/workflows/daily-archive.yml`
* Runs every day at **07:00 UTC**

To enable it:

1. Push this repo to your own GitHub account.
2. Make sure GitHub Actions is enabled for the repository.
3. That’s it — the archive will run daily in the cloud.

---

## 📄 Output Example

CSV output (`all_articles_YYYY-MM-DD.csv`):

| Newspaper URL                                                | Archive Request Time |
| ------------------------------------------------------------ | -------------------- |
| [https://www.prothom-alo.com](https://www.prothom-alo.com)   | 2025-07-10 09:35:12  |
| [https://www.banglanews24.com](https://www.banglanews24.com) | 2025-07-10 09:35:30  |

---

## 📋 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.

You are free to:

* ✅ Share, use, and modify the code
* ✅ Use it for **academic, research, or personal purposes**
* ❌ **Commercial or for-profit use is not permitted**

Full license text: [https://creativecommons.org/licenses/by-nc/4.0/legalcode](https://creativecommons.org/licenses/by-nc/4.0/legalcode)

---

## 🤝 Contributions & Support

* Pull requests are welcome!
* Suggest improvements, new newspapers, or bug fixes via [GitHub Issues](https://github.com/md-k-sarker/news-archiver/issues).

---

## 📢 Disclaimer

This tool interacts with Archive.today, a third-party archiving service. Archival success depends on the availability and behavior of that service. The project does not guarantee successful archiving or bypassing of any security on source websites.


---

## 📬 Contact

Questions? Email the maintainer or open an issue in the repository.

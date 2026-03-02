# 🥕 Data-Driven Retail Insights (Instacart)
### Cost Savings & Revenue Growth through Machine Learning

This project analyzes the Instacart Online Grocery Basket dataset (3M+ orders, 200K+ users) to extract actionable retail intelligence using Exploratory Data Analysis, Association Rule Mining (FP-Growth), Customer Segmentation, and Revenue Simulation.

The objective is not only to understand customer behavior, but to quantify the financial impact of applying these insights in a real retail environment.

---

## 📌 Project Scope

This project follows a complete retail analytics pipeline:

### 🔍 1. Exploratory Data Analysis (EDA)
- Order distribution by weekday and hour  
- Product distribution by aisle and department  
- Customer order frequency  
- Purchase behavior per user  

### 💰 2. Synthetic Pricing Integration
- Generated synthetic product prices (dataset has no price data)  
- Enabled revenue estimation and financial simulations  

### 🛒 3. Association Rule Mining (FP-Growth)
- Frequent itemsets using **FP-Growth**  
- Key metrics: **Support, Confidence, Lift**  
- Product relationships analyzed by department and aisle  
- Identification of high-lift bundle opportunities  

### 🧠 4. Customer Segmentation
- Sparse binary encoding of orders  
- **TruncatedSVD** for dimensionality reduction  
- **MiniBatchKMeans** for clustering  
- Segment profiling by department preference  

### 📈 5. Revenue & Pricing Simulation
- Revenue estimation using synthetic prices  
- Simulation of:
  - Bundle-driven revenue growth  
  - Cross-selling impact  
  - Promotion efficiency  
- Financial comparison between baseline and optimized strategy  

---

## 📊 Instacart Analytics Dashboard

An interactive Streamlit dashboard presenting four core analytics views:

- ⏰ **Busiest Hours** – Peak shopping time distribution  
- 📅 **Busiest Days** – Weekly order trends  
- 📊 **Customer Segment Distribution** – Order volume by cluster  
- 🏬 **Segment Department Profile** – Department preferences by segment  

The dashboard translates machine learning outputs into clear, business-ready visual insights.

---

## 📈 Business Impact

- **Increase Average Order Value (AOV):** Identify high-lift product bundles for cross-selling  
- **Targeted Marketing:** Leverage customer segmentation for personalized campaigns  
- **Operational Optimization:** Align staffing and inventory with peak shopping periods  
- **Revenue Simulation:** Estimate financial gains from bundling and pricing strategies  

---

## 🛠️ Installation & Usage

### 1️⃣ Prerequisites

- Python 3.9 or higher  
- pip (Python package manager)

---

### 2️⃣ Clone the Repository

```bash
git clone <https://github.com/grocery-saving-team/Grocery-Saving-Solution.git>
cd Grocery-Saving-Solution
```

---

### 3️⃣ Set Up Virtual Environment (Recommended)

#### MacOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
.\venv\Scripts\activate
```

---

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 5️⃣ Run the Application

```bash
streamlit run app.py
```

After running the command, open the local URL shown in the terminal (usually: `http://localhost:8501`).

---

## 📦 Core Stack

| Library          | Usage                                      |
|------------------|--------------------------------------------|
| **Python**       | Programming language                       |
|**Streamlit**     | UI Framework & Deployment                  |
| **Pandas**       | Data Manipulation & Analysis               |
| **NumPy**        | Numerical Computation                      |
| **Scikit-Learn** | ML Pipeline (TruncatedSVD & KMeans)        |
|**FP-Growth**     |Association rule mining                     |
| **Plotly**       | Interactive Data Visualizations            |

---

## 👩‍💻 Author

Developed as an end-to-end Machine Learning & Analytics dashboard using the Instacart dataset.
Team 2 of class: Machine Learning with Python Labs of DSTI 2025
- Dinh Duy TRAN
- Doreen Chepkoech KOSKE
- Kim Yen LE
- Leonardo Mariano HERNANDEZ ECHENIQUE
- Myat Noe WAI
- Nona Shamila SALLAY
- Viet Linh Vu


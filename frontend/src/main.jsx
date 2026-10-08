import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import "./style.css";

const API = "https://ai-sales-intelligence-crm.onrender.com";

async function api(path, opts = {}) {
  const token = localStorage.getItem("token");

  const response = await fetch(API + path, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(token
        ? { Authorization: "Bearer " + token }
        : {}),
      ...(opts.headers || {}),
    },
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json();
}


/* =========================
   LOGIN
========================= */
function Login({ onLogin }) {
  const [mode, setMode] = useState("login");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("sales_rep");

  const [err, setErr] = useState("");
  const [success, setSuccess] = useState("");

  async function submit(e) {
    e.preventDefault();

    setErr("");
    setSuccess("");

    try {
      if (mode === "login") {
        const result = await api("/auth/login", {
          method: "POST",
          body: JSON.stringify({
            email,
            password,
          }),
        });

        localStorage.setItem(
          "token",
          result.access_token
        );

        onLogin();
      } else {
        await api("/auth/register", {
          method: "POST",
          body: JSON.stringify({
            name,
            email,
            password,
            role,
          }),
        });

        setSuccess(
          "Account created successfully. Signing you in..."
        );

        const result = await api("/auth/login", {
          method: "POST",
          body: JSON.stringify({
            email,
            password,
          }),
        });

        localStorage.setItem(
          "token",
          result.access_token
        );

        onLogin();
      }
    } catch (error) {
      console.error(error);

      setErr(
        mode === "login"
          ? "Invalid email or password"
          : "Registration failed. Email may already be registered."
      );
    }
  }

  function switchMode() {
    setMode(
      mode === "login"
        ? "register"
        : "login"
    );

    setErr("");
    setSuccess("");

    setName("");
    setEmail("");
    setPassword("");
  }

  return (
    <div className="login">
      <div className="card login-card">

        <div className="logo-circle">
          S
        </div>

        <h1>SalesIQ</h1>

        <p>
          AI Sales Intelligence & CRM
        </p>

        <h2>
          {mode === "login"
            ? "Welcome back"
            : "Create your account"}
        </h2>

        <form onSubmit={submit}>

          {mode === "register" && (
            <input
              value={name}
              onChange={(e) =>
                setName(e.target.value)
              }
              placeholder="Full name"
              type="text"
              required
            />
          )}

          <input
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            placeholder="Email"
            type="email"
            required
          />

          <input
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            placeholder="Password"
            type="password"
            required
          />

          {mode === "register" && (
            <select
              value={role}
              onChange={(e) =>
                setRole(e.target.value)
              }
            >
              <option value="sales_rep">
                Sales Representative
              </option>

              <option value="sales_manager">
                Sales Manager
              </option>
            </select>
          )}

          <button
            className="primary-button full-width"
            type="submit"
          >
            {mode === "login"
              ? "Sign in"
              : "Create account"}
          </button>

        </form>

        {err && (
          <div className="error-message">
            {err}
          </div>
        )}

        {success && (
          <div className="success-message">
            {success}
          </div>
        )}

        <button
          type="button"
          className="text-button"
          onClick={switchMode}
        >
          {mode === "login"
            ? "New here? Create an account"
            : "Already have an account? Sign in"}
        </button>

      </div>
    </div>
  );
}



/* =========================
   MAIN APP
========================= */

function App() {

  const [logged, setLogged] =
    useState(
      !!localStorage.getItem("token")
    );

  const [tab, setTab] =
    useState("Dashboard");

  const [data, setData] =
    useState(null);

  const [leads, setLeads] =
    useState([]);

  const [customers, setCustomers] =
    useState([]);

  const [deals, setDeals] =
    useState([]);

  const [activities, setActivities] =
    useState([]);

  const [q, setQ] =
    useState("");

  const [answer, setAnswer] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [showLeadForm, setShowLeadForm] =
    useState(false);

  const [showCustomerForm, setShowCustomerForm] =
    useState(false);

  const [showDealForm, setShowDealForm] =
    useState(false);

  const [showActivityForm, setShowActivityForm] =
    useState(false);


  /* =========================
     FORMS
  ========================= */

  const [leadForm, setLeadForm] =
    useState({
      name: "",
      email: "",
      company_name: "",
      source: "website",
      industry: "technology",
      estimated_value: "",
    });

  const [customerForm, setCustomerForm] =
    useState({
      company_name: "",
      contact_name: "",
      email: "",
      phone: "",
      industry: "",
      location: "",
      annual_revenue: "",
    });

  const [dealForm, setDealForm] =
    useState({
      name: "",
      customer_id: "",
      value: "",
      stage: "prospecting",
    });

  const [activityForm, setActivityForm] =
    useState({
      customer_id: "",
      lead_id: "",
      deal_id: "",
      activity_type: "call",
      description: "",
      due_date: "",
    });


  /* =========================
     ML DEAL PREDICTION
  ========================= */

  async function predictDeal(
    dealValue,
    stage,
    leadScore = 50,
    activityCount = 0
  ) {
    try {

      const result = await api(
        "/deals/predict",
        {
          method: "POST",

          body: JSON.stringify({
            deal_value: Number(
              dealValue
            ),

            stage,

            lead_score: Number(
              leadScore
            ),

            activity_count: Number(
              activityCount
            ),
          }),
        }
      );

      return result.win_probability;

    } catch (error) {

      console.error(
        "ML prediction failed:",
        error
      );

      return null;
    }
  }


  /* =========================
     LOAD DATA
  ========================= */

  async function load() {

    try {

      setLoading(true);

      const [
        dashboardData,
        leadsData,
        customersData,
        dealsData,
        activitiesData,
      ] = await Promise.all([

        api("/dashboard"),

        api("/leads/"),

        api("/customers/"),

        api("/deals/"),

        api("/activities/"),

      ]);

      setData(
        dashboardData
      );

      setLeads(
        leadsData
      );

      setCustomers(
        customersData
      );

      setActivities(
        activitiesData
      );


      /* Add ML prediction to every deal */

      const enrichedDeals =
        await Promise.all(

          dealsData.map(
            async (deal) => {

              const activityCount =
                activitiesData.filter(
                  (activity) =>
                    activity.deal_id ===
                    deal.id
                ).length;

              const mlProbability =
                await predictDeal(
                  deal.value,
                  deal.stage,
                  50,
                  activityCount
                );

              return {
                ...deal,
                ml_probability:
                  mlProbability,
              };
            }
          )
        );

      setDeals(
        enrichedDeals
      );

    } catch (error) {

      console.error(error);

      localStorage.removeItem(
        "token"
      );

      setLogged(false);

    } finally {

      setLoading(false);
    }
  }


  useEffect(() => {

    if (logged) {
      load();
    }

  }, [logged]);


  /* =========================
     LOGOUT
  ========================= */

  function logout() {

    localStorage.removeItem(
      "token"
    );

    setLogged(false);

    setData(null);

    setLeads([]);

    setCustomers([]);

    setDeals([]);

    setActivities([]);
  }


  /* =========================
     CREATE LEAD
  ========================= */

  async function createLead(e) {

    e.preventDefault();

    try {

      await api("/leads/", {
        method: "POST",

        body: JSON.stringify({
          ...leadForm,

          estimated_value:
            Number(
              leadForm.estimated_value
            ),
        }),
      });

      setLeadForm({
        name: "",
        email: "",
        company_name: "",
        source: "website",
        industry: "technology",
        estimated_value: "",
      });

      setShowLeadForm(false);

      await load();

    } catch (error) {

      console.error(error);

      alert(
        "Unable to create lead."
      );
    }
  }


  /* =========================
     CREATE CUSTOMER
  ========================= */

  async function createCustomer(e) {

    e.preventDefault();

    try {

      await api("/customers/", {
        method: "POST",

        body: JSON.stringify({
          ...customerForm,

          annual_revenue:
            customerForm.annual_revenue
              ? Number(
                  customerForm.annual_revenue
                )
              : null,
        }),
      });

      setCustomerForm({
        company_name: "",
        contact_name: "",
        email: "",
        phone: "",
        industry: "",
        location: "",
        annual_revenue: "",
      });

      setShowCustomerForm(false);

      await load();

    } catch (error) {

      console.error(error);

      alert(
        "Unable to create customer."
      );
    }
  }


  /* =========================
     CREATE DEAL
  ========================= */

  async function createDeal(e) {

    e.preventDefault();

    try {

      const mlProbability =
        await predictDeal(
          dealForm.value,
          dealForm.stage,
          50,
          0
        );

      const createdDeal =
        await api("/deals/", {
          method: "POST",

          body: JSON.stringify({
            name:
              dealForm.name,

            customer_id:
              dealForm.customer_id
                ? Number(
                    dealForm.customer_id
                  )
                : null,

            value:
              Number(
                dealForm.value
              ),

            stage:
              dealForm.stage,
          }),
        });

      setDeals(
        (previous) => [
          ...previous,

          {
            ...createdDeal,

            ml_probability:
              mlProbability,
          },
        ]
      );

      setDealForm({
        name: "",
        customer_id: "",
        value: "",
        stage: "prospecting",
      });

      setShowDealForm(false);

      const dashboardData =
        await api(
          "/dashboard"
        );

      setData(
        dashboardData
      );

    } catch (error) {

      console.error(error);

      alert(
        "Unable to create deal."
      );
    }
  }


  /* =========================
     CREATE ACTIVITY
  ========================= */

  async function createActivity(e) {

    e.preventDefault();

    try {

      await api(
        "/activities/",
        {
          method: "POST",

          body: JSON.stringify({

            customer_id:
              activityForm.customer_id
                ? Number(
                    activityForm.customer_id
                  )
                : null,

            lead_id:
              activityForm.lead_id
                ? Number(
                    activityForm.lead_id
                  )
                : null,

            deal_id:
              activityForm.deal_id
                ? Number(
                    activityForm.deal_id
                  )
                : null,

            activity_type:
              activityForm.activity_type,

            description:
              activityForm.description,

            due_date:
              activityForm.due_date
                ? new Date(
                    activityForm.due_date
                  ).toISOString()
                : null,
          }),
        }
      );

      setActivityForm({
        customer_id: "",
        lead_id: "",
        deal_id: "",
        activity_type: "call",
        description: "",
        due_date: "",
      });

      setShowActivityForm(
        false
      );

      await load();

    } catch (error) {

      console.error(error);

      alert(
        "Unable to create activity."
      );
    }
  }


  /* =========================
     COPILOT
  ========================= */

  async function ask() {

    if (!q.trim()) return;

    try {

      setAnswer(
        "Thinking..."
      );

      const result =
        await api(
          "/copilot",
          {
            method: "POST",

            body: JSON.stringify({
              question: q,
            }),
          }
        );

      setAnswer(
        result.answer
      );

    } catch (error) {

      console.error(error);

      setAnswer(
        "Unable to get an answer."
      );
    }
  }


  /* =========================
     FORMATTING
  ========================= */

  function formatCurrency(value) {

    if (!value) {
      return "₹0";
    }

    if (value >= 10000000) {

      return (
        "₹" +
        (
          value / 10000000
        ).toFixed(2) +
        "Cr"
      );
    }

    if (value >= 100000) {

      return (
        "₹" +
        (
          value / 100000
        ).toFixed(2) +
        "L"
      );
    }

    if (value >= 1000) {

      return (
        "₹" +
        (
          value / 1000
        ).toFixed(1) +
        "K"
      );
    }

    return (
      "₹" +
      Number(value).toLocaleString(
        "en-IN"
      )
    );
  }


  function formatDate(date) {

    if (!date) {
      return "No date";
    }

    return new Date(
      date
    ).toLocaleString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }
    );
  }


  /* =========================
     LOGIN SCREEN
  ========================= */

  if (!logged) {

    return (
      <Login
        onLogin={() =>
          setLogged(true)
        }
      />
    );
  }


  /* =========================
     DASHBOARD VALUES
  ========================= */

  const totalLeads =
    data?.leads?.total ?? 0;

  const totalCustomers =
    data?.customers?.total ?? 0;

  const totalDeals =
    data?.deals?.total ?? 0;

  const highPriorityLeads =
    data?.leads?.high_priority ?? 0;

  const pipelineValue =
    data?.deals?.pipeline_value ?? 0;

  const weightedPipelineValue =
    data?.deals
      ?.weighted_pipeline_value ?? 0;

  const wonRevenue =
    data?.deals?.won_revenue ?? 0;

  const lostRevenue =
    data?.deals?.lost_revenue ?? 0;

  const averageProbability =
    data?.deals
      ?.average_probability ?? 0;

  const pendingActivities =
    data?.activities?.pending ?? 0;

  const completedActivities =
    data?.activities?.completed ?? 0;


  /* =========================
     CHART DATA
  ========================= */

  const chartData =
    leads
      .slice(0, 8)
      .map((lead) => ({
        name: lead.name,
        score: lead.lead_score,
      }));

  const pipelineChart = [
    {
      name: "Pipeline",
      value: pipelineValue,
    },

    {
      name: "Weighted",
      value: weightedPipelineValue,
    },

    {
      name: "Won",
      value: wonRevenue,
    },

    {
      name: "Lost",
      value: lostRevenue,
    },
  ];

  const leadPriorityData = [
    {
      name: "High",
      value:
        highPriorityLeads,
    },

    {
      name: "Other",
      value:
        Math.max(
          totalLeads -
            highPriorityLeads,
          0
        ),
    },
  ];

  const activityData = [
    {
      name: "Pending",
      value:
        pendingActivities,
    },

    {
      name: "Completed",
      value:
        completedActivities,
    },
  ];


  /* =========================
     UI
  ========================= */

  return (

    <div className="app">

      {/* SIDEBAR */}

      <aside>

        <div className="brand">
          <div className="brand-icon">
            S
          </div>

          <div>
            <h2>SalesIQ</h2>

            <span>
              Sales Intelligence
            </span>
          </div>
        </div>


        <nav>

          {[
            "Dashboard",
            "Leads",
            "Deals",
            "Customers",
            "Activities",
            "AI Copilot",
          ].map((item) => (

            <button
              key={item}
              className={
                tab === item
                  ? "active"
                  : ""
              }
              onClick={() =>
                setTab(item)
              }
            >

              <span>
                {item ===
                  "Dashboard" && "▦"}

                {item ===
                  "Leads" && "◉"}

                {item ===
                  "Deals" && "◆"}

                {item ===
                  "Customers" && "◌"}

                {item ===
                  "Activities" && "✓"}

                {item ===
                  "AI Copilot" && "✦"}
              </span>

              {item}

            </button>

          ))}

        </nav>


        <button
          className="logout"
          onClick={logout}
        >
          ↪ Logout
        </button>

      </aside>


      {/* MAIN */}

      <main>

        <header>

          <div>

            <h1>
              {tab}
            </h1>

            <span>
              AI Sales Intelligence &
              CRM
            </span>

          </div>

          <div className="header-status">
            <span className="online-dot"></span>
            System Online
          </div>

        </header>


        {loading && (

          <div className="panel loading-panel">

            <div className="spinner"></div>

            <p>
              Loading sales intelligence...
            </p>

          </div>

        )}


        {/* =========================
            DASHBOARD
        ========================= */}

        {tab === "Dashboard" &&
          data &&
          !loading && (

            <>

              <div className="grid">

                <div className="metric">

                  <span>
                    Total Leads
                  </span>

                  <strong>
                    {totalLeads}
                  </strong>

                  <small>
                    Active opportunities
                  </small>

                </div>


                <div className="metric">

                  <span>
                    Customers
                  </span>

                  <strong>
                    {totalCustomers}
                  </strong>

                  <small>
                    Managed accounts
                  </small>

                </div>


                <div className="metric">

                  <span>
                    Deals
                  </span>

                  <strong>
                    {totalDeals}
                  </strong>

                  <small>
                    Sales opportunities
                  </small>

                </div>


                <div className="metric">

                  <span>
                    Pipeline
                  </span>

                  <strong>
                    {formatCurrency(
                      pipelineValue
                    )}
                  </strong>

                  <small>
                    Total opportunity value
                  </small>

                </div>


                <div className="metric">

                  <span>
                    Weighted Pipeline
                  </span>

                  <strong>
                    {formatCurrency(
                      weightedPipelineValue
                    )}
                  </strong>

                  <small>
                    Probability-adjusted
                  </small>

                </div>


                <div className="metric">

                  <span>
                    Avg. Win Probability
                  </span>

                  <strong>
                    {averageProbability}%
                  </strong>

                  <small>
                    Current deal portfolio
                  </small>

                </div>

              </div>


              <div className="dashboard-grid">


                {/* PIPELINE */}

                <div className="panel chart-panel">

                  <div className="panel-heading">

                    <div>

                      <h3>
                        Pipeline Overview
                      </h3>

                      <p>
                        Revenue opportunity
                        across the sales funnel.
                      </p>

                    </div>

                  </div>


                  <ResponsiveContainer
                    width="100%"
                    height={300}
                  >

                    <BarChart
                      data={pipelineChart}
                      margin={{
                        top: 15,
                        right: 20,
                        left: 60,
                        bottom: 10,
                      }}
                    >

                      <XAxis
                        dataKey="name"
                      />

                      <YAxis
                        width={60}
                        tickFormatter={(value) =>
                          formatCurrency(
                            value
                          )
                        }
                      />

                      <Tooltip
                        formatter={(value) =>
                          formatCurrency(
                            Number(value)
                          )
                        }
                      />

                      <Bar
                        dataKey="value"
                        fill="#2563eb"
                        radius={[
                          6,
                          6,
                          0,
                          0,
                        ]}
                      />

                    </BarChart>

                  </ResponsiveContainer>

                </div>


                {/* LEAD PRIORITY */}

                <div className="panel chart-panel">

                  <div className="panel-heading">

                    <div>

                      <h3>
                        Lead Priority
                      </h3>

                      <p>
                        AI-ranked lead distribution.
                      </p>

                    </div>

                  </div>


                  <ResponsiveContainer
                    width="100%"
                    height={300}
                  >

                    <PieChart>

                      <Pie
                        data={
                          leadPriorityData
                        }
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="45%"
                        outerRadius={90}
                        label
                      >

                        {leadPriorityData.map(
                          (_, index) => (

                            <Cell
                              key={index}
                              fill={
                                index === 0
                                  ? "#ef4444"
                                  : "#cbd5e1"
                              }
                            />

                          )
                        )}

                      </Pie>

                      <Tooltip />

                      <Legend />

                    </PieChart>

                  </ResponsiveContainer>

                </div>

              </div>


              <div className="dashboard-grid">


                {/* SALES INTELLIGENCE */}

                <div className="panel chart-panel">

                  <div className="panel-heading">

                    <div>

                      <h3>
                        Sales Intelligence
                      </h3>

                      <p>
                        Lead scores ranked by
                        business potential.
                      </p>

                    </div>

                  </div>


                  {chartData.length >
                  0 ? (

                    <ResponsiveContainer
                      width="100%"
                      height={300}
                    >

                      <BarChart
                        data={chartData}
                        margin={{
                          top: 15,
                          right: 20,
                          left: 60,
                          bottom: 10,
                        }}
                      >

                        <XAxis
                          dataKey="name"
                        />

                        <YAxis
                          width={60}
                        />

                        <Tooltip />

                        <Bar
                          dataKey="score"
                          name="Lead Score"
                          fill="#2563eb"
                          radius={[
                            6,
                            6,
                            0,
                            0,
                          ]}
                        />

                      </BarChart>

                    </ResponsiveContainer>

                  ) : (

                    <div className="empty-state">
                      No leads available.
                    </div>

                  )}

                </div>


                {/* ACTIVITY */}

                <div className="panel chart-panel">

                  <div className="panel-heading">

                    <div>

                      <h3>
                        Activity Status
                      </h3>

                      <p>
                        Follow-up execution status.
                      </p>

                    </div>

                  </div>


                  <ResponsiveContainer
                    width="100%"
                    height={300}
                  >

                    <PieChart>

                      <Pie
                        data={
                          activityData
                        }
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="45%"
                        outerRadius={90}
                        label
                      >

                        {activityData.map(
                          (_, index) => (

                            <Cell
                              key={index}
                              fill={
                                index === 0
                                  ? "#f59e0b"
                                  : "#22c55e"
                              }
                            />

                          )
                        )}

                      </Pie>

                      <Tooltip />

                      <Legend />

                    </PieChart>

                  </ResponsiveContainer>

                </div>

              </div>


              {/* SUMMARY METRICS */}

              <div className="grid">

                <div className="metric">

                  <span>
                    Won Revenue
                  </span>

                  <strong>
                    {formatCurrency(
                      wonRevenue
                    )}
                  </strong>

                  <small>
                    Closed-won deals
                  </small>

                </div>


                <div className="metric">

                  <span>
                    Lost Revenue
                  </span>

                  <strong>
                    {formatCurrency(
                      lostRevenue
                    )}
                  </strong>

                  <small>
                    Closed-lost deals
                  </small>

                </div>


                <div className="metric">

                  <span>
                    Pending Follow-ups
                  </span>

                  <strong>
                    {pendingActivities}
                  </strong>

                  <small>
                    Require attention
                  </small>

                </div>


                <div className="metric">

                  <span>
                    Completed Activities
                  </span>

                  <strong>
                    {completedActivities}
                  </strong>

                  <small>
                    Sales actions completed
                  </small>

                </div>

              </div>

            </>

          )}


        {/* =========================
            LEADS
        ========================= */}

        {tab === "Leads" && (

          <div className="panel">

            <div className="section-header">

              <div>

                <h3>
                  Lead Prioritization
                </h3>

                <p>
                  AI-ranked leads based on
                  business value and source
                  quality.
                </p>

              </div>

              <button
                className="primary-button"
                onClick={() =>
                  setShowLeadForm(
                    !showLeadForm
                  )
                }
              >
                {showLeadForm
                  ? "Cancel"
                  : "+ Add Lead"}
              </button>

            </div>


            {showLeadForm && (

              <form
                className="crm-form"
                onSubmit={createLead}
              >

                <input
                  placeholder="Lead name"
                  value={leadForm.name}
                  onChange={(e) =>
                    setLeadForm({
                      ...leadForm,
                      name:
                        e.target.value,
                    })
                  }
                  required
                />

                <input
                  placeholder="Email"
                  type="email"
                  value={leadForm.email}
                  onChange={(e) =>
                    setLeadForm({
                      ...leadForm,
                      email:
                        e.target.value,
                    })
                  }
                  required
                />

                <input
                  placeholder="Company"
                  value={
                    leadForm.company_name
                  }
                  onChange={(e) =>
                    setLeadForm({
                      ...leadForm,
                      company_name:
                        e.target.value,
                    })
                  }
                  required
                />

                <select
                  value={
                    leadForm.source
                  }
                  onChange={(e) =>
                    setLeadForm({
                      ...leadForm,
                      source:
                        e.target.value,
                    })
                  }
                >

                  <option value="website">
                    Website
                  </option>

                  <option value="referral">
                    Referral
                  </option>

                  <option value="linkedin">
                    LinkedIn
                  </option>

                  <option value="email">
                    Email
                  </option>

                  <option value="cold_call">
                    Cold Call
                  </option>

                </select>


                <input
                  placeholder="Industry"
                  value={
                    leadForm.industry
                  }
                  onChange={(e) =>
                    setLeadForm({
                      ...leadForm,
                      industry:
                        e.target.value,
                    })
                  }
                  required
                />


                <input
                  placeholder="Estimated deal value"
                  type="number"
                  value={
                    leadForm.estimated_value
                  }
                  onChange={(e) =>
                    setLeadForm({
                      ...leadForm,
                      estimated_value:
                        e.target.value,
                    })
                  }
                  required
                />


                <button
                  className="primary-button"
                  type="submit"
                >
                  Create Lead
                </button>

              </form>

            )}


            {leads.length === 0 ? (

              <div className="empty-state">
                No leads found.
              </div>

            ) : (

              <div className="table-wrapper">

                <table>

                  <thead>

                    <tr>
                      <th>Lead</th>
                      <th>Company</th>
                      <th>Source</th>
                      <th>Value</th>
                      <th>Score</th>
                      <th>Priority</th>
                    </tr>

                  </thead>

                  <tbody>

                    {leads.map(
                      (lead) => (

                        <tr
                          key={
                            lead.id
                          }
                        >

                          <td>
                            <strong>
                              {
                                lead.name
                              }
                            </strong>
                          </td>

                          <td>
                            {
                              lead.company_name
                            }
                          </td>

                          <td>
                            {
                              lead.source
                            }
                          </td>

                          <td>
                            ₹
                            {Number(
                              lead.estimated_value ||
                                0
                            ).toLocaleString(
                              "en-IN"
                            )}
                          </td>

                          <td>
                            {
                              lead.lead_score
                            }
                          </td>

                          <td>

                            <span
                              className={
                                "pill " +
                                lead.priority
                              }
                            >
                              {
                                lead.priority
                              }
                            </span>

                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            )}

          </div>

        )}


        {/* =========================
            DEALS
        ========================= */}

        {tab === "Deals" && (

          <div className="panel">

            <div className="section-header">

              <div>

                <h3>
                  Sales Pipeline
                </h3>

                <p>
                  Track opportunities and
                  AI-estimated win probability.
                </p>

              </div>

              <button
                className="primary-button"
                onClick={() =>
                  setShowDealForm(
                    !showDealForm
                  )
                }
              >
                {showDealForm
                  ? "Cancel"
                  : "+ Add Deal"}
              </button>

            </div>


            {showDealForm && (

              <form
                className="crm-form"
                onSubmit={createDeal}
              >

                <input
                  placeholder="Deal name"
                  value={dealForm.name}
                  onChange={(e) =>
                    setDealForm({
                      ...dealForm,
                      name:
                        e.target.value,
                    })
                  }
                  required
                />


                <select
                  value={
                    dealForm.customer_id
                  }
                  onChange={(e) =>
                    setDealForm({
                      ...dealForm,
                      customer_id:
                        e.target.value,
                    })
                  }
                >

                  <option value="">
                    Select customer
                  </option>

                  {customers.map(
                    (customer) => (

                      <option
                        key={
                          customer.id
                        }
                        value={
                          customer.id
                        }
                      >
                        {
                          customer.company_name
                        }
                      </option>

                    )
                  )}

                </select>


                <input
                  placeholder="Deal value"
                  type="number"
                  value={dealForm.value}
                  onChange={(e) =>
                    setDealForm({
                      ...dealForm,
                      value:
                        e.target.value,
                    })
                  }
                  required
                />


                <select
                  value={
                    dealForm.stage
                  }
                  onChange={(e) =>
                    setDealForm({
                      ...dealForm,
                      stage:
                        e.target.value,
                    })
                  }
                >

                  <option value="prospecting">
                    Prospecting
                  </option>

                  <option value="qualification">
                    Qualification
                  </option>

                  <option value="proposal">
                    Proposal
                  </option>

                  <option value="negotiation">
                    Negotiation
                  </option>

                  <option value="closed_won">
                    Closed Won
                  </option>

                  <option value="closed_lost">
                    Closed Lost
                  </option>

                </select>


                <button
                  className="primary-button"
                  type="submit"
                >
                  Create Deal
                </button>

              </form>

            )}


            {deals.length === 0 ? (

              <div className="empty-state">
                No deals found.
              </div>

            ) : (

              <div className="table-wrapper">

                <table>

                  <thead>

                    <tr>
                      <th>Deal</th>
                      <th>Customer</th>
                      <th>Value</th>
                      <th>Stage</th>
                      <th>Stage Probability</th>
                      <th>ML Win Probability</th>
                      <th>ML Weighted Value</th>
                    </tr>

                  </thead>

                  <tbody>

                    {deals.map(
                      (deal) => {

                        const customer =
                          customers.find(
                            (item) =>
                              item.id ===
                              deal.customer_id
                          );

                        const mlProbability =
                          deal.ml_probability;

                        const mlWeighted =
                          mlProbability !==
                            null &&
                          mlProbability !==
                            undefined
                            ? Number(
                                deal.value ||
                                  0
                              ) *
                              Number(
                                mlProbability
                              ) /
                              100
                            : null;

                        return (

                          <tr
                            key={
                              deal.id
                            }
                          >

                            <td>
                              <strong>
                                {
                                  deal.name
                                }
                              </strong>
                            </td>

                            <td>
                              {customer
                                ? customer.company_name
                                : "Unassigned"}
                            </td>

                            <td>
                              {formatCurrency(
                                deal.value
                              )}
                            </td>

                            <td>

                              <span className="stage">
                                {deal.stage.replace(
                                  "_",
                                  " "
                                )}
                              </span>

                            </td>

                            <td>
                              <strong>
                                {
                                  deal.probability
                                }%
                              </strong>
                            </td>

                            <td>

                              {mlProbability !==
                                null &&
                              mlProbability !==
                                undefined ? (

                                <span className="ml-score">
                                  {
                                    mlProbability
                                  }%
                                </span>

                              ) : (
                                "-"
                              )}

                            </td>

                            <td>

                              {mlWeighted !==
                              null
                                ? formatCurrency(
                                    mlWeighted
                                  )
                                : "-"}

                            </td>

                          </tr>

                        );
                      }
                    )}

                  </tbody>

                </table>

              </div>

            )}

          </div>

        )}


        {/* =========================
            CUSTOMERS
        ========================= */}

        {tab === "Customers" && (

          <div className="panel">

            <div className="section-header">

              <div>

                <h3>
                  Customer Management
                </h3>

                <p>
                  Manage customer accounts and
                  business information.
                </p>

              </div>

              <button
                className="primary-button"
                onClick={() =>
                  setShowCustomerForm(
                    !showCustomerForm
                  )
                }
              >
                {showCustomerForm
                  ? "Cancel"
                  : "+ Add Customer"}
              </button>

            </div>


            {showCustomerForm && (

              <form
                className="crm-form"
                onSubmit={
                  createCustomer
                }
              >

                <input
                  placeholder="Company name"
                  value={
                    customerForm.company_name
                  }
                  onChange={(e) =>
                    setCustomerForm({
                      ...customerForm,
                      company_name:
                        e.target.value,
                    })
                  }
                  required
                />


                <input
                  placeholder="Contact name"
                  value={
                    customerForm.contact_name
                  }
                  onChange={(e) =>
                    setCustomerForm({
                      ...customerForm,
                      contact_name:
                        e.target.value,
                    })
                  }
                  required
                />


                <input
                  placeholder="Email"
                  type="email"
                  value={
                    customerForm.email
                  }
                  onChange={(e) =>
                    setCustomerForm({
                      ...customerForm,
                      email:
                        e.target.value,
                    })
                  }
                  required
                />


                <input
                  placeholder="Phone"
                  value={
                    customerForm.phone
                  }
                  onChange={(e) =>
                    setCustomerForm({
                      ...customerForm,
                      phone:
                        e.target.value,
                    })
                  }
                />


                <input
                  placeholder="Industry"
                  value={
                    customerForm.industry
                  }
                  onChange={(e) =>
                    setCustomerForm({
                      ...customerForm,
                      industry:
                        e.target.value,
                    })
                  }
                />


                <input
                  placeholder="Location"
                  value={
                    customerForm.location
                  }
                  onChange={(e) =>
                    setCustomerForm({
                      ...customerForm,
                      location:
                        e.target.value,
                    })
                  }
                />


                <input
                  placeholder="Annual revenue"
                  type="number"
                  value={
                    customerForm.annual_revenue
                  }
                  onChange={(e) =>
                    setCustomerForm({
                      ...customerForm,
                      annual_revenue:
                        e.target.value,
                    })
                  }
                />


                <button
                  className="primary-button"
                  type="submit"
                >
                  Create Customer
                </button>

              </form>

            )}


            {customers.length ===
            0 ? (

              <div className="empty-state">
                No customers found.
              </div>

            ) : (

              <div className="table-wrapper">

                <table>

                  <thead>

                    <tr>
                      <th>Company</th>
                      <th>Contact</th>
                      <th>Email</th>
                      <th>Industry</th>
                      <th>Location</th>
                      <th>Revenue</th>
                      <th>Status</th>
                    </tr>

                  </thead>

                  <tbody>

                    {customers.map(
                      (customer) => (

                        <tr
                          key={
                            customer.id
                          }
                        >

                          <td>
                            <strong>
                              {
                                customer.company_name
                              }
                            </strong>
                          </td>

                          <td>
                            {
                              customer.contact_name
                            }
                          </td>

                          <td>
                            {
                              customer.email
                            }
                          </td>

                          <td>
                            {
                              customer.industry ||
                              "-"
                            }
                          </td>

                          <td>
                            {
                              customer.location ||
                              "-"
                            }
                          </td>

                          <td>

                            {customer.annual_revenue
                              ? formatCurrency(
                                  customer.annual_revenue
                                )
                              : "-"}

                          </td>

                          <td>

                            <span className="status-active">
                              {
                                customer.status
                              }
                            </span>

                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            )}

          </div>

        )}


        {/* =========================
            ACTIVITIES
        ========================= */}

        {tab === "Activities" && (

          <div className="panel">

            <div className="section-header">

              <div>

                <h3>
                  Sales Activities
                </h3>

                <p>
                  Schedule calls, meetings and
                  follow-ups.
                </p>

              </div>

              <button
                className="primary-button"
                onClick={() =>
                  setShowActivityForm(
                    !showActivityForm
                  )
                }
              >
                {showActivityForm
                  ? "Cancel"
                  : "+ Add Activity"}
              </button>

            </div>


            {showActivityForm && (

              <form
                className="crm-form"
                onSubmit={
                  createActivity
                }
              >

                <select
                  value={
                    activityForm.activity_type
                  }
                  onChange={(e) =>
                    setActivityForm({
                      ...activityForm,
                      activity_type:
                        e.target.value,
                    })
                  }
                >

                  <option value="call">
                    Call
                  </option>

                  <option value="email">
                    Email
                  </option>

                  <option value="meeting">
                    Meeting
                  </option>

                  <option value="follow_up">
                    Follow-up
                  </option>

                  <option value="demo">
                    Demo
                  </option>

                </select>


                <select
                  value={
                    activityForm.customer_id
                  }
                  onChange={(e) =>
                    setActivityForm({
                      ...activityForm,
                      customer_id:
                        e.target.value,
                    })
                  }
                >

                  <option value="">
                    Customer
                  </option>

                  {customers.map(
                    (customer) => (

                      <option
                        key={
                          customer.id
                        }
                        value={
                          customer.id
                        }
                      >
                        {
                          customer.company_name
                        }
                      </option>

                    )
                  )}

                </select>


                <select
                  value={
                    activityForm.lead_id
                  }
                  onChange={(e) =>
                    setActivityForm({
                      ...activityForm,
                      lead_id:
                        e.target.value,
                    })
                  }
                >

                  <option value="">
                    Lead
                  </option>

                  {leads.map(
                    (lead) => (

                      <option
                        key={lead.id}
                        value={lead.id}
                      >
                        {lead.name}
                      </option>

                    )
                  )}

                </select>


                <select
                  value={
                    activityForm.deal_id
                  }
                  onChange={(e) =>
                    setActivityForm({
                      ...activityForm,
                      deal_id:
                        e.target.value,
                    })
                  }
                >

                  <option value="">
                    Deal
                  </option>

                  {deals.map(
                    (deal) => (

                      <option
                        key={deal.id}
                        value={deal.id}
                      >
                        {deal.name}
                      </option>

                    )
                  )}

                </select>


                <input
                  type="datetime-local"
                  value={
                    activityForm.due_date
                  }
                  onChange={(e) =>
                    setActivityForm({
                      ...activityForm,
                      due_date:
                        e.target.value,
                    })
                  }
                />


                <input
                  placeholder="Activity description"
                  value={
                    activityForm.description
                  }
                  onChange={(e) =>
                    setActivityForm({
                      ...activityForm,
                      description:
                        e.target.value,
                    })
                  }
                  required
                />


                <button
                  className="primary-button"
                  type="submit"
                >
                  Create Activity
                </button>

              </form>

            )}


            {activities.length ===
            0 ? (

              <div className="empty-state">
                No activities found.
              </div>

            ) : (

              <div className="table-wrapper">

                <table>

                  <thead>

                    <tr>
                      <th>Type</th>
                      <th>Description</th>
                      <th>Due Date</th>
                      <th>Status</th>
                    </tr>

                  </thead>

                  <tbody>

                    {activities.map(
                      (activity) => (

                        <tr
                          key={
                            activity.id
                          }
                        >

                          <td>

                            <span className="stage">
                              {
                                activity.activity_type
                              }
                            </span>

                          </td>

                          <td>
                            {
                              activity.description
                            }
                          </td>

                          <td>
                            {formatDate(
                              activity.due_date
                            )}
                          </td>

                          <td>

                            <span
                              className={
                                activity.completed
                                  ? "status-active"
                                  : "status-pending"
                              }
                            >

                              {activity.completed
                                ? "Completed"
                                : "Pending"}

                            </span>

                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            )}

          </div>

        )}


        {/* =========================
            AI COPILOT
        ========================= */}

        {tab === "AI Copilot" && (

          <div className="panel copilot">

            <div className="copilot-header">

              <div className="copilot-icon">
                ✦
              </div>

              <div>

                <h3>
                  AI Sales Copilot
                </h3>

                <p>
                  Ask questions about your sales
                  pipeline, leads, customers and
                  follow-ups.
                </p>

              </div>

            </div>


            <div className="chips">

              {[
                "Which leads should I call today?",
                "What is our current pipeline?",
                "Which deals are most likely to close?",
                "Which leads have the highest value?",
                "How many customers do we have?",
                "What follow-ups are pending?",
              ].map(
                (question) => (

                  <button
                    key={question}
                    onClick={() =>
                      setQ(question)
                    }
                  >
                    {question}
                  </button>

                )
              )}

            </div>


            <textarea
              value={q}
              onChange={(e) =>
                setQ(
                  e.target.value
                )
              }
              placeholder="Ask a sales question..."
            />


            <button
              className="primary-button"
              onClick={ask}
            >
              Ask Copilot
            </button>


            {answer && (

              <div className="answer">

                <div className="answer-title">
                  AI Recommendation
                </div>

                {answer}

              </div>

            )}

          </div>

        )}

      </main>

    </div>
  );
}


createRoot(
  document.getElementById("root")
).render(
  <App />
);
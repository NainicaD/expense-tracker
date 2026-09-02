import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Expense Splitter", page_icon="💸", layout="centered")

if "people" not in st.session_state:
    st.session_state.people = []
if "expenses" not in st.session_state:
    st.session_state.expenses = []
if "form_version" not in st.session_state:
    st.session_state.form_version = 0
if "pending_toast" not in st.session_state:
    st.session_state.pending_toast = None

if st.session_state.pending_toast:
    st.toast(st.session_state.pending_toast, icon="✅")
    st.session_state.pending_toast = None

PRIMARY = "#6C5CE7"
PRIMARY_SOFT = "#F5F3FF"
INK = "#1E1B2E"
INK_MUTED = "#8A8698"
GRIDLINE = "#E7E4F2"

st.markdown(
    f"""
    <style>
    .block-container {{
        padding-top: 2.5rem;
        max-width: 760px;
    }}
    h1 {{
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }}
    h2 {{
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: {INK} !important;
        margin-top: 0 !important;
    }}
    .subtitle {{
        color: {INK_MUTED};
        margin-top: -0.6rem;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
    }}
    .section-card {{
        background: #FFFFFF;
        border: 1px solid {GRIDLINE};
        border-radius: 16px;
        padding: 1.4rem 1.5rem 1.5rem 1.5rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 1px 3px rgba(30, 27, 46, 0.04);
    }}
    .person-pill button {{
        border-radius: 999px !important;
        border: 1px solid {GRIDLINE} !important;
        background: {PRIMARY_SOFT} !important;
        color: {INK} !important;
        font-size: 0.85rem !important;
        padding: 0.15rem 0.9rem !important;
    }}
    .person-pill button:hover {{
        border-color: {PRIMARY} !important;
        color: {PRIMARY} !important;
    }}
    div[data-testid="stForm"], .unit-card {{
        border-radius: 12px !important;
    }}
    button[kind="primary"] {{
        border-radius: 10px !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stMetric"] {{
        background: {PRIMARY_SOFT};
        border-radius: 14px;
        padding: 0.9rem 1rem 0.7rem 1rem;
        border: 1px solid {GRIDLINE};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💸 Splitwise-lite")
st.markdown('<div class="subtitle">Track shared expenses and see who owes what.</div>', unsafe_allow_html=True)

tab_people, tab_add, tab_expenses, tab_summary = st.tabs(
    ["👥 People", "➕ Add expense", "🧾 Expenses", "💰 Summary"]
)

# ---------- People ----------
with tab_people:
    st.header("People")
    with st.form("add_person_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_person = st.text_input(
                "Add a person", key="new_person_input", label_visibility="collapsed",
                placeholder="Enter a name and press Add",
            )
        with col2:
            added = st.form_submit_button("Add", use_container_width=True)

        if added:
            name = new_person.strip()
            if name and name not in st.session_state.people:
                st.session_state.people.append(name)
                st.rerun()

    if st.session_state.people:
        st.write("")
        chips = st.columns(min(len(st.session_state.people), 4))
        for i, person in enumerate(st.session_state.people):
            with chips[i % len(chips)]:
                st.markdown('<div class="person-pill">', unsafe_allow_html=True)
                if st.button(f"{person}  ✕", key=f"remove_{person}", use_container_width=True):
                    st.session_state.people.remove(person)
                    for exp in st.session_state.expenses:
                        for unit in exp["units"]:
                            if person in unit["people"]:
                                unit["people"].remove(person)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Add at least one person to start tracking expenses.")

# ---------- Add expense ----------
with tab_add:
    st.header("Add an expense")

    if not st.session_state.people:
        st.warning("Add people in the **People** tab before adding expenses.")
    else:
        v = st.session_state.form_version

        item_name = st.text_input("Item name", key=f"item_name_{v}", placeholder="e.g. Dustbin")
        col_qty, col_price = st.columns(2)
        with col_qty:
            quantity = st.number_input("Quantity", min_value=1, max_value=50, value=1, step=1, key=f"quantity_{v}")
        with col_price:
            unit_price = st.number_input(
                "Price per item" if quantity > 1 else "Price",
                min_value=0.0, step=0.01, format="%.2f", key=f"unit_price_{v}",
            )

        st.caption(
            "For each item, choose whether it's split between everyone or specific people — "
            "e.g. one dustbin charged to one person, a second dustbin split between two others."
        )

        units_people = []
        for i in range(int(quantity)):
            label = f"Item {i + 1} of {int(quantity)}" if quantity > 1 else "Split between"
            mode_key = f"unit_mode_{v}_{i}"
            people_key = f"unit_people_{v}_{i}"

            with st.container(border=True):
                st.markdown(f"**{label}**")
                mode = st.radio(
                    "Split type", ["Everyone", "Specific people"],
                    horizontal=True, key=mode_key, label_visibility="collapsed",
                )
                if mode == "Everyone":
                    units_people.append(list(st.session_state.people))
                else:
                    chosen = st.multiselect("Choose people", st.session_state.people, key=people_key)
                    units_people.append(list(chosen))

        if st.button("Add expense", type="primary"):
            errors = []
            if not item_name.strip():
                errors.append("Please enter an item name.")
            if unit_price <= 0:
                errors.append("Please enter a price greater than 0.")
            for i, people in enumerate(units_people):
                if not people:
                    which = f"Item {i + 1}" if quantity > 1 else "the split"
                    errors.append(f"Please choose at least one person for {which}.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                st.session_state.expenses.append({
                    "item": item_name.strip(),
                    "unit_price": float(unit_price),
                    "units": [{"people": people} for people in units_people],
                })
                st.session_state.form_version += 1
                st.session_state.pending_toast = f"**{item_name.strip()}** added (${unit_price:.2f} x {int(quantity)})"
                st.rerun()

# ---------- Expenses table ----------
with tab_expenses:
    st.header("Expenses")

    if not st.session_state.expenses:
        st.info("No expenses yet — add one in the **Add expense** tab.")
    else:
        rows = []
        for idx, exp in enumerate(st.session_state.expenses):
            multi_unit = len(exp["units"]) > 1
            for u_idx, unit in enumerate(exp["units"]):
                n = len(unit["people"])
                per_person = exp["unit_price"] / n if n else 0
                item_label = f"{exp['item']} ({u_idx + 1}/{len(exp['units'])})" if multi_unit else exp["item"]
                rows.append({
                    "Item": item_label,
                    "Price": exp["unit_price"],
                    "Split between": ", ".join(unit["people"]) if unit["people"] else "—",
                    "# People": n,
                    "Per person": per_person,
                })

        df = pd.DataFrame(rows)
        st.dataframe(
            df, use_container_width=True, hide_index=True,
            column_config={
                "Price": st.column_config.NumberColumn(format="$%.2f"),
                "Per person": st.column_config.NumberColumn(format="$%.2f"),
            },
        )

        remove_idx = st.selectbox(
            "Remove an expense (removes all units of that item)",
            options=list(range(len(st.session_state.expenses))),
            format_func=lambda i: (
                f"{st.session_state.expenses[i]['item']} "
                f"(${st.session_state.expenses[i]['unit_price']:.2f} x {len(st.session_state.expenses[i]['units'])})"
            ),
        )
        if st.button("Remove selected expense"):
            st.session_state.expenses.pop(remove_idx)
            st.rerun()

# ---------- Totals per person ----------
with tab_summary:
    st.header("Who owes what")

    if not st.session_state.people:
        st.info("Add people to see totals.")
    else:
        totals = {person: 0.0 for person in st.session_state.people}
        for exp in st.session_state.expenses:
            for unit in exp["units"]:
                n = len(unit["people"])
                if n == 0:
                    continue
                share = exp["unit_price"] / n
                for person in unit["people"]:
                    totals[person] += share

        grand_total = sum(exp["unit_price"] * len(exp["units"]) for exp in st.session_state.expenses)
        st.metric("Grand total of all expenses", f"${grand_total:.2f}")
        st.write("")

        totals_df = pd.DataFrame(
            [{"Person": person, "Amount": amount} for person, amount in totals.items()]
        ).sort_values("Amount", ascending=False)

        if grand_total > 0:
            max_amount = totals_df["Amount"].max()
            bar = (
                alt.Chart(totals_df)
                .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, size=22, color=PRIMARY)
                .encode(
                    x=alt.X(
                        "Amount:Q", title=None,
                        scale=alt.Scale(domain=[0, max_amount * 1.18]),
                        axis=alt.Axis(grid=False, labels=False, ticks=False, domain=False),
                    ),
                    y=alt.Y("Person:N", sort="-x", title=None, axis=alt.Axis(labelColor=INK, labelFontSize=13)),
                    tooltip=[alt.Tooltip("Person:N"), alt.Tooltip("Amount:Q", format="$.2f")],
                )
            )
            labels = bar.mark_text(
                align="left", dx=6, color=INK, fontWeight="bold", fontSize=13,
            ).encode(text=alt.Text("Amount:Q", format="$.2f"))

            chart = (bar + labels).properties(height=44 * len(totals_df) + 10)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.dataframe(
                totals_df.rename(columns={"Amount": "Total owed"}),
                use_container_width=True, hide_index=True,
                column_config={"Total owed": st.column_config.NumberColumn(format="$%.2f")},
            )

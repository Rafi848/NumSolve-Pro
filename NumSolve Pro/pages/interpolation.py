import streamlit as st
import pandas as pd
import numpy as np
import math

st.set_page_config(
    page_title="Interpolation Methods - NumSolve Pro",
    page_icon="",
    layout="wide"
)

# Custom CSS for NumSolve Pro styling
st.markdown("""
<style>

/* Hide Streamlit Default UI Elements */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Custom Headers */
.main-title {
    text-align: center;
    font-size: 40px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 5px;
}
.sub-title {
    text-align: center;
    font-size: 18px;
    color: #38bdf8;
    margin-bottom: 25px;
}

/* Step container box */
.step-box {
    background-color: #1e293b;
    border-left: 4px solid #38bdf8;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HELPER FUNCTIONS: VALIDATION, DIFFERENCE TABLE & INTERPOLATION ENGINES
# ==============================================================================

def validate_interpolation_inputs(df, selected_method, target_x):
    """
    Validates input dataframe and returns (is_valid, error_message, x_array, y_array).
    """
    try:
        x_vals = df["x"].values
        y_vals = df["f(x)"].values

        if np.isnan(x_vals).any() or np.isnan(y_vals).any():
            return False, "Data table contains empty or invalid numeric cells. Please enter valid numbers.", None, None

        if len(x_vals) < 2:
            return False, "At least 2 data points are required for interpolation.", None, None

        if selected_method == "Linear Interpolation" and len(x_vals) < 2:
            return False, "Linear Interpolation requires at least 2 points.", None, None

        if len(x_vals) != len(set(x_vals)):
            return False, "Duplicate 'x' values detected! All 'x' values must be unique.", None, None

        x_list = [float(val) for val in x_vals]
        y_list = [float(val) for val in y_vals]

        if selected_method in ["Newton Forward", "Newton Backward"]:
            intervals = np.diff(x_list)
            if not np.allclose(intervals, intervals[0], atol=1e-5):
                return False, (
                    f"**{selected_method}** requires **equally spaced** 'x' values.<br>"
                    f"Current spacings are: `{list(np.round(intervals, 4))}`.<br>"
                    f"💡 *Tip: Try **Lagrange** or **Newton Divided Difference** for unequally spaced data.*"
                ), None, None

        return True, "Valid", np.array(x_list), np.array(y_list)

    except Exception as e:
        return False, f"An unexpected error occurred while parsing inputs: {str(e)}", None, None


def compute_forward_diff_matrix(x_vals, y_vals):
    """
    Computes full Forward Difference matrix and returns:
    1. 2D numpy array containing numerical difference table
    2. Formatted pandas DataFrame for UI rendering
    """
    n = len(x_vals)
    table = np.zeros((n, n))
    table[:, 0] = y_vals
    
    for j in range(1, n):
        for i in range(n - j):
            table[i][j] = table[i + 1][j - 1] - table[i][j - 1]

    col_names = ["x", "f(x)"] + [f"Δ^{j}f" if j > 1 else "Δf" for j in range(1, n)]
    
    display_matrix = []
    for i in range(n):
        row = [f"{x_vals[i]:.4f}", f"{y_vals[i]:.4f}"]
        for j in range(1, n):
            if i < n - j:
                row.append(f"{table[i][j]:.4f}")
            else:
                row.append("")
        display_matrix.append(row)

    df_display = pd.DataFrame(display_matrix, columns=col_names)
    return table, df_display


def newton_forward_interpolation(x_vals, y_vals, target_x, diff_table):
    """
    Calculates Newton Forward Interpolation step by step.
    """
    n = len(x_vals)
    x0 = x_vals[0]
    h = x_vals[1] - x_vals[0]
    u = (target_x - x0) / h
    
    terms_info = []
    u_product = 1.0
    
    term_0 = diff_table[0][0]
    terms_info.append({
        "order": 0,
        "label": "y_0",
        "u_numeric": 1.0,
        "diff_val": term_0,
        "factorial": 1,
        "term_val": term_0
    })
    
    result = term_0
    
    for k in range(1, n):
        u_product *= (u - (k - 1))
        diff_val = diff_table[0][k]
        fact_val = math.factorial(k)
        term_val = (u_product * diff_val) / fact_val
        
        terms_info.append({
            "order": k,
            "label": f"\\Delta^{k}y_0" if k > 1 else "\\Delta y_0",
            "u_numeric": u_product,
            "diff_val": diff_val,
            "factorial": fact_val,
            "term_val": term_val
        })
        result += term_val
        
    return h, u, terms_info, result


def newton_backward_interpolation(x_vals, y_vals, target_x, diff_table):
    """
    Calculates Newton Backward Interpolation step by step.
    """
    n = len(x_vals)
    xn = x_vals[-1]
    h = x_vals[1] - x_vals[0]
    u = (target_x - xn) / h
    
    terms_info = []
    u_product = 1.0
    
    term_0 = diff_table[n - 1][0]
    terms_info.append({
        "order": 0,
        "label": "y_n",
        "u_numeric": 1.0,
        "diff_val": term_0,
        "factorial": 1,
        "term_val": term_0
    })
    
    result = term_0
    
    for k in range(1, n):
        u_product *= (u + (k - 1))
        diff_val = diff_table[n - 1 - k][k]
        fact_val = math.factorial(k)
        term_val = (u_product * diff_val) / fact_val
        
        terms_info.append({
            "order": k,
            "label": f"\\nabla^{k}y_n" if k > 1 else "\\nabla y_n",
            "u_numeric": u_product,
            "diff_val": diff_val,
            "factorial": fact_val,
            "term_val": term_val
        })
        result += term_val
        
    return h, u, xn, terms_info, result


def lagrange_interpolation(x_vals, y_vals, target_x):
    """
    Calculates Lagrange Interpolation step by step.
    """
    n = len(x_vals)
    l_info = []
    final_result = 0.0

    for i in range(n):
        num = 1.0
        den = 1.0
        num_terms = []
        den_terms = []

        for j in range(n):
            if i != j:
                num *= (target_x - x_vals[j])
                den *= (x_vals[i] - x_vals[j])
                num_terms.append(f"({target_x:.4f} - {x_vals[j]:.4f})")
                den_terms.append(f"({x_vals[i]:.4f} - {x_vals[j]:.4f})")

        l_i = num / den
        term_val = y_vals[i] * l_i
        final_result += term_val

        l_info.append({
            "index": i,
            "x_i": x_vals[i],
            "y_i": y_vals[i],
            "num_val": num,
            "den_val": den,
            "num_str": " × ".join(num_terms),
            "den_str": " × ".join(den_terms),
            "l_i": l_i,
            "term_val": term_val
        })

    return l_info, final_result


# ==============================================================================
# UI LAYOUT
# ==============================================================================

# Page Branding
st.markdown('<div class="main-title"> Interpolation Methods</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">NumSolve Pro — Advanced Numerical Methods Simulator</div>', unsafe_allow_html=True)

st.markdown("---")

# Layout: Section 1 - Selection Controls
col_method, col_points = st.columns([1, 1], gap="medium")

with col_method:
    st.subheader(" Method Selection")
    selected_method = st.selectbox(
        "Select Interpolation Method",
        [
            "Linear Interpolation",
            "Newton Forward",
            "Newton Backward",
            "Lagrange",
            "Newton Divided Difference"
        ],
        index=3
    )

with col_points:
    st.subheader(" Data Points Count")
    num_points = st.number_input(
        "Number of Data Points:",
        min_value=2,
        max_value=20,
        value=5,
        step=1
    )

st.markdown("---")

# Layout: Section 2 - Data Input Table & Target Value
st.subheader("Data Table & Target Value")

col_table, col_target = st.columns([2, 1], gap="medium")

with col_table:
    st.markdown("**Enter $(x, f(x))$ Data Pairs:**")
    
    default_x = [float(i) for i in range(1, num_points + 1)]
    default_y = [float(x**2) for x in default_x]

    df_default = pd.DataFrame({
        "x": default_x,
        "f(x)": default_y
    })

    edited_df = st.data_editor(
        df_default,
        num_rows="fixed",
        use_container_width=True,
        key="interpolation_editor"
    )

with col_target:
    st.markdown("**Target Point:**")
    target_x = st.number_input(
        "Target x value:",
        value=2.5,
        format="%.4f"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    calculate_button = st.button(
        " CALCULATE INTERPOLATION",
        use_container_width=True,
        type="primary"
    )

# ==============================================================================
# CALCULATION & STEP-BY-STEP OUTPUT
# ==============================================================================

if calculate_button:
    # Run Validation
    is_valid, msg, x_data, y_data = validate_interpolation_inputs(edited_df, selected_method, target_x)
    
    if not is_valid:
        st.error(msg, icon="🚨")
    else:
        st.success(" Input Data Passed All Validation Checks!", icon="🎉")
        
        # Summary Card
        st.markdown("###  Processed Input Summary")
        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
        
        with col_res1:
            st.metric("Selected Method", selected_method)
        with col_res2:
            st.metric("Total Points (n)", len(x_data))
        with col_res3:
            st.metric("Target x", f"{target_x:.4f}")
        with col_res4:
            is_equal = "Yes" if np.allclose(np.diff(x_data), np.diff(x_data)[0]) else "No"
            st.metric("Equally Spaced x?", is_equal)

        if target_x < min(x_data) or target_x > max(x_data):
            st.warning(
                f"⚠️ **Extrapolation Warning:** Target $x = {target_x}$ lies outside domain "
                f"[{min(x_data)}, {max(x_data)}]. Accuracy may decrease.",
                icon="⚠️"
            )

        st.markdown("---")

        # Compute Difference Matrix for Forward and Backward
        diff_matrix, df_diff_display = compute_forward_diff_matrix(x_data, y_data)

        if selected_method in ["Newton Forward", "Newton Backward"]:
            st.subheader("📐 Finite Difference Table")
            st.dataframe(df_diff_display, use_container_width=True, hide_index=True)
            st.markdown("---")

        # EXECUTE NEWTON FORWARD
        if selected_method == "Newton Forward":
            st.subheader(" Step-by-Step Calculation — Newton Forward Interpolation")
            
            h, u, terms, final_result = newton_forward_interpolation(x_data, y_data, target_x, diff_matrix)
            
            st.latex(r"""
            P(x) = y_0 + u \Delta y_0 + \frac{u(u-1)}{2!} \Delta^2 y_0 + \frac{u(u-1)(u-2)}{3!} \Delta^3 y_0 + \dots
            """)

            st.markdown(f"""
            <div class="step-box">
                <h4>STEP 1 — Calculate Step Size (h)</h4>
                $$h = x_1 - x_0 = {x_data[1]:.4f} - {x_data[0]:.4f} = {h:.4f}$$
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="step-box">
                <h4>STEP 2 — Calculate Parameter (u)</h4>
                $$u = \\frac{{x - x_0}}{{h}} = \\frac{{{target_x:.4f} - {x_data[0]:.4f}}}{{{h:.4f}}} = {u:.4f}$$
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### STEP 3 — Individual Terms Calculation")
            terms_df_list = []
            for t in terms:
                terms_df_list.append({
                    "Term": f"Term {t['order']}",
                    "Formula / Symbol": f"${t['label']}$",
                    "Numerator (u-product × Δ)": f"{t['u_numeric']:.4f} × {t['diff_val']:.4f}",
                    "Denominator (k!)": f"{t['factorial']}! = {t['factorial']}",
                    "Term Value": f"{t['term_val']:.6f}"
                })
            st.table(pd.DataFrame(terms_df_list))

            st.markdown("#### STEP 4 — Final Summation")
            terms_sum_str = " + ".join([f"{t['term_val']:.4f}" for t in terms])
            st.markdown(f"$$P({target_x}) = {terms_sum_str}$$")

            st.success(
                f" **Interpolated Result:** $f({target_x:.4f}) \\approx \\mathbf{{{final_result:.6f}}}$",
                icon="💡"
            )

        # EXECUTE NEWTON BACKWARD
        elif selected_method == "Newton Backward":
            st.subheader(" Step-by-Step Calculation — Newton Backward Interpolation")
            
            h, u, xn, terms, final_result = newton_backward_interpolation(x_data, y_data, target_x, diff_matrix)
            
            st.latex(r"""
            P(x) = y_n + u \nabla y_n + \frac{u(u+1)}{2!} \nabla^2 y_n + \frac{u(u+1)(u+2)}{3!} \nabla^3 y_n + \dots
            """)

            st.markdown(f"""
            <div class="step-box">
                <h4>STEP 1 — Calculate Step Size (h)</h4>
                $$h = x_n - x_{{n-1}} = {x_data[-1]:.4f} - {x_data[-2]:.4f} = {h:.4f}$$
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="step-box">
                <h4>STEP 2 — Calculate Parameter (u)</h4>
                $$u = \\frac{{x - x_n}}{{h}} = \\frac{{{target_x:.4f} - {xn:.4f}}}{{{h:.4f}}} = {u:.4f}$$
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### STEP 3 — Individual Terms Calculation")
            terms_df_list = []
            for t in terms:
                terms_df_list.append({
                    "Term": f"Term {t['order']}",
                    "Formula / Symbol": f"${t['label']}$",
                    "Numerator (u-product × ∇)": f"{t['u_numeric']:.4f} × {t['diff_val']:.4f}",
                    "Denominator (k!)": f"{t['factorial']}! = {t['factorial']}",
                    "Term Value": f"{t['term_val']:.6f}"
                })
            st.table(pd.DataFrame(terms_df_list))

            st.markdown("#### STEP 4 — Final Summation")
            terms_sum_str = " + ".join([f"{t['term_val']:.4f}" for t in terms])
            st.markdown(f"$$P({target_x}) = {terms_sum_str}$$")

            st.success(
                f" **Interpolated Result:** $f({target_x:.4f}) \\approx \\mathbf{{{final_result:.6f}}}$",
                icon="💡"
            )

        # EXECUTE LAGRANGE
        elif selected_method == "Lagrange":
            st.subheader(" Step-by-Step Calculation — Lagrange Interpolation")
            
            l_info, final_result = lagrange_interpolation(x_data, y_data, target_x)
            
            st.latex(r"""
            P(x) = \sum_{i=0}^{n-1} y_i \cdot L_i(x) \quad \text{where} \quad L_i(x) = \prod_{j=0, j \neq i}^{n-1} \frac{x - x_j}{x_i - x_j}
            """)

            # STEP 1: Basis Polynomial breakdown
            st.markdown("#### STEP 1 — Lagrange Basis Polynomials $L_i(x)$")
            
            lagrange_table_list = []
            for item in l_info:
                lagrange_table_list.append({
                    "i": item["index"],
                    "x_i": f"{item['x_i']:.4f}",
                    "y_i": f"{item['y_i']:.4f}",
                    "Numerator": f"{item['num_val']:.6f}",
                    "Denominator": f"{item['den_val']:.6f}",
                    "L_i(x) = Num/Den": f"{item['l_i']:.6f}",
                    "Weighted Term (y_i × L_i)": f"{item['term_val']:.6f}"
                })

            st.table(pd.DataFrame(lagrange_table_list))

            # STEP 2: Mathematical expansion detail
            st.markdown("#### STEP 2 — Detailed Fraction Expansion")
            for item in l_info:
                st.markdown(f"""
                <div class="step-box">
                    <b>L_{{{item['index']}}}({target_x:.4f})</b> = 
                    $$\\frac{{{item['num_str']}}}{{{item['den_str']}}} = \\frac{{{item['num_val']:.6f}}}{{{item['den_val']:.6f}}} = \\mathbf{{{item['l_i']:.6f}}}$$
                    <br>
                    <b>Term {item['index']} Value:</b> $y_{{{item['index']}}} \\times L_{{{item['index']}}}({target_x:.4f}) = {item['y_i']:.4f} \\times {item['l_i']:.6f} = \\mathbf{{{item['term_val']:.6f}}}$
                </div>
                """, unsafe_allow_html=True)

            # STEP 3: Final Summation
            st.markdown("#### STEP 3 — Final Summation")
            terms_sum_str = " + ".join([f"{item['term_val']:.6f}" for item in l_info])
            st.markdown(f"$$P({target_x:.4f}) = {terms_sum_str}$$")

            # Final Answer Banner
            st.success(
                f" **Interpolated Result:** $f({target_x:.4f}) \\approx \\mathbf{{{final_result:.6f}}}$",
                icon="💡"
            )

        else:
            st.info(f"The calculation engine for **{selected_method}** will be activated in upcoming parts.")
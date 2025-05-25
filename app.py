# created on March 10, 2025

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import os

#STart to commit 23May2025 to GitHub
# ---- PAGE CONFIGURATION ----

st.set_page_config(page_title="dbSPT Dashboard", layout="wide")

# ---- HIDE STREAMLIT STYLE ----
# hide_st_style = """
# <style>
# #MainMenu {visibility: hidden;}
# footer {visibility: hidden;}
# header {visibility: hidden;}
# </style>
# """
# st.markdown(hide_st_style, unsafe_allow_html=True)

# Fungsi untuk mengubah gambar menjadi base64
def get_image_as_base64(image_path):
	with open(image_path, "rb") as img_file:
		return base64.b64encode(img_file.read()).decode()

# ---- APP TITLE ----

kiri, kanan = st.columns([3, 2])
with kiri:
    st.markdown(
        """
        <h3 style='text-align: left; color: #333;'> 📊 dbSPT Dashboard</h1>
        <h5 style='text-align: left; color: #666;'>Spareparts & Tools Summary Report</h2>
        """,
        unsafe_allow_html=True
    )
with kanan: # Menampilkan logo di kolom kanan
        
        # Menggunakan os.path untuk mendapatkan path gambar        
        # Adjust the file path based on the current directory
		current_dir = os.path.dirname(os.path.abspath(__file__))
		logo_KPD = os.path.join(current_dir, 'logoKPD.png')
		# Memuat gambar dan mengubahnya menjadi base64
		# logo_KPD ='logoKPD.png'
		image_base64 = get_image_as_base64(logo_KPD)
		
		# Menampilkan gambar dan teks di kolom kanan dengan posisi berdampingan
		st.markdown(
			f"""
			<style>
			.container {{
				display: flex;
				align-items:center;
				justify-content: flex-end;
				flex-wrap: wrap;
			}}
			.container img {{
				width: 50px;
				margin-top: -20px;
			}}
			.container h2 {{
				color: grey;
				font-size: 20px;
				margin-top: -20px;
				margin-right: 10px;
				margin-bottom: 0px;
			}}
			@media (min-width: 600px) {{
				.container {{
					justify-content: center;
				}}
				.container img {{
					margin-top: 0;
				}}
				.container h2 {{
					margin-top: 0;
					text-align: center;
				}}
			}}
			</style>
			<div class="container">
				<h2 style="color:blue;">PT. KARYAPRATAMA DUNIA</h2>
				<img src='data:image/png;base64,{image_base64}'/>
			</div>
			""",
			unsafe_allow_html=True
		)

		st.markdown("---")

    
# ---- APP DESCRIPTION ----
header_col1, header_col2 = st.columns([1, 1])
with header_col1:
    st.markdown(
        """
        <h5 style='font-size:0.9rem;text-align: left; color: #666;'>Aplikasi ini digunakan untuk menganalisis data spareparts dan tools. Data bersumber dari File Excel yang diinput secara rutin oleh team produksi Stamping Line PT. KARYAPRATAMA DUNIA</h5>
       
        <div style='padding:1rem; border:1px solid #ddd; border-radius:1rem; text-align:center;'>
                <div style='font-size:0.9rem; color:brown; font-weight:bold'>Disclaimer: </div>
                <div style='font-size:0.8rem; color:gray;'>Sumber data excel hanya bisa diuload dari Aplikasi dbSPT.xlsm yang ada di PT. KARYAPRATAMA DUNIA</div>
            """, unsafe_allow_html=True)
    
with header_col2:
    st.markdown(
        """
        <h5 style='text-align: left; color: #666;'>Silahkan unggah file Excel (.xlsx / .xlsm) </h5>
        """,
        unsafe_allow_html=True
    )


    uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx", "xlsm"])

if uploaded_file:
    try:
        # Baca sheet "USAGE" dan kolom B:K
        df = pd.read_excel(uploaded_file, sheet_name="USAGE", usecols="B:K")

        # Bersihkan nama kolom
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()

        # Tampilkan data original dalam expander (cascade style)
        with st.expander("📄 Lihat Data Asli"): #(Kolom B–K dari Sheet 'USAGE')
            st.dataframe(df, use_container_width=True)


        # Pastikan kolom Date ada
        if 'Date' not in df.columns:
            st.warning("❌ Kolom 'Date' tidak ditemukan. Pastikan kolom 'Date' ada pada kolom B–K.")
            st.stop()

        # Konversi kolom Date ke datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)

        # Buat kolom Bulan-Tahun
        df['Bulan-Tahun'] = df['Date'].dt.strftime('%B %Y')

        # Urutkan Bulan-Tahun berdasarkan tanggal termuda ke tertua
        bulan_tahun_order = df.sort_values('Date',ascending=False)['Bulan-Tahun'].drop_duplicates().tolist()
        bulan_tahun_options = bulan_tahun_order
       

        #hilangkan whitespace di depan dan belakang pada kolom PIC
        df['PIC'] = df['PIC'].str.strip()

        #ubah isi kolom PIC menjadi huruf besar semua
        df['PIC'] = df['PIC'].str.upper()

        # st.divider()
        st.write("📅 Filter Data berdasarkan Bulan-Tahun")
        selected_bt = st.multiselect("Pilih satu atau beberapa Bulan-Tahun", bulan_tahun_options, default=bulan_tahun_options[:1])

        # Filter DataFrame
        filtered_df = df[df['Bulan-Tahun'].isin(selected_bt)]

        st.success(f"Menampilkan {len(filtered_df)} baris untuk bulan-tahun: {', '.join(selected_bt)}")

        # Download hasil filter
        def convert_df_to_excel(dataframe):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                dataframe.drop(columns=['Bulan-Tahun']).to_excel(writer, index=False, sheet_name='USAGE Filtered')
            return output.getvalue()

        excel_data = convert_df_to_excel(filtered_df)

        file_name = "USAGE_filtered.xlsx"
        if selected_bt:
            joined = "_".join(bt.replace(" ", "_") for bt in selected_bt)
            file_name = f"USAGE_{joined}.xlsx"


        emma_L, emma_R = st.columns([1, 1])
        with emma_L:
            with st.expander("📄 Tampilkan Data Hasil Filtering"):
                st.dataframe(filtered_df.drop(columns=['Bulan-Tahun']), use_container_width=True)
        with emma_R:
            st.download_button(
                label="📥 Download Hasil Filter",
                data=excel_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.markdown("---")

        kol1, kol2, kol3    = st.columns(3)
        # Tampilkan total Qty dan Amount
        with kol1:
            st.subheader("📈 SUMMARY DATA")
        
        with kol2:
            total_amount = filtered_df['Total Amount'].sum()
            total_amount_str = f"{total_amount:,.0f}"
            st.markdown(f"""
            <div style='padding:1rem; border:1px solid #ddd; border-radius:1rem; text-align:center;'>
                <div style='font-size:0.9rem; color:gray;'>Total Amount [IDR]</div>
                <div style='font-size:1.8rem; font-weight:bold;'>{total_amount_str}</div>
            """, unsafe_allow_html=True)
            
        with kol3:
            total_qty = filtered_df['Qty'].sum()
            total_qty_str = f"{total_qty:,.0f}"
            st.markdown(f"""
            <div style='padding:1rem; border:1px solid #ddd; border-radius:1rem; text-align:center;'>
                <div style='font-size:0.9rem; color:gray;'>Total Qty [pcs]</div>
                <div style='font-size:1.8rem; font-weight:bold;'>{total_qty_str}</div>
            """, unsafe_allow_html=True)
     

        # Visualisasi data

        st.write("📈 Visualisasi Data")
        st.write("Grafik interaktif untuk analisis data spareparts dan tools.")

#region Adaptasi Date
       # Konversi kolom Date
        filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

        # Agregasi bulanan
        filtered_df['Month-Year'] = filtered_df['Date'].dt.strftime('%b %Y')
        monthly_summary = (
            filtered_df.groupby('Month-Year')
            .agg({'Qty': 'sum', 'Total Amount': 'sum'})
            .reset_index()
        )
        monthly_summary['SortDate'] = pd.to_datetime(monthly_summary['Month-Year'], format='%b %Y')
        monthly_summary = monthly_summary.sort_values('SortDate')

#endregion Adaptasi Date

#region Grafik Line Harian by M/C No.
        # Grafik Line Harian by M/C No. ---
        # Buat chart fig1
        # Filter data berdasarkan bulan-tahun
        if selected_bt:
            selected_date = pd.to_datetime(selected_bt[0], format='%B %Y')
            start_date = selected_date.replace(day=1)
            end_date = start_date + pd.offsets.MonthEnd(1)

            # Buat rentang tanggal harian
            daily_range = pd.date_range(start=start_date, end=end_date)

            # Ambil data tanggal dalam rentang ini
            filtered_dates = filtered_df[
                (filtered_df['Date'] >= start_date) &
                (filtered_df['Date'] <= end_date)
            ]

            # Ambil semua kombinasi tanggal × M/C
            unique_mcs = filtered_dates['M/C No.'].unique()
            full_index = pd.MultiIndex.from_product([daily_range, unique_mcs], names=['Date', 'M/C No.'])

            # Hitung jumlah per hari & M/C
            daily_amount_mc = (
                filtered_dates.groupby(['Date', 'M/C No.'])['Total Amount']
                .sum()
                .reindex(full_index, fill_value=0)  # Pastikan semua kombinasi ada
                .reset_index()
                .sort_values('Date')
            )
        else:
            daily_amount_mc = pd.DataFrame()

        # Buat grafik

        fig2 = go.Figure()
        for mc in daily_amount_mc['M/C No.'].unique():
            df_mc = daily_amount_mc[daily_amount_mc['M/C No.'] == mc]
            fig2.add_trace(go.Scatter(
                x=df_mc['Date'],
                y=df_mc['Total Amount'],
                mode='lines+markers',
                name=mc
            ))

        fig2.update_layout(
            title="Chart Amount [IDR] by Daily Data (M/C No.)",
            xaxis=dict(
                title="Date",
                tickformat="%d %b %Y",
                tickangle=45
            ),
            yaxis=dict(
                title="Total Amount [IDR]",
                tickformat=","
            ),
            hovermode='x unified',
            legend=dict(
                title="M/C No.",
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1
            ),
            margin=dict(t=60, b=80)
        )

        st.plotly_chart(fig2, use_container_width=True)

#endregion Grafik Line Harian by M/C No.

#region Grafik Bar Qty dan Amount by Month-Year 

        # Grafik Bar Qty dan Amount by Month-Year ---
        # Buat grafik bar untuk Qty dan Total Amount

        fig1 = go.Figure()

        # Bar Qty
        fig1.add_trace(go.Bar(
            x=monthly_summary['Month-Year'],
            y=monthly_summary['Qty'],
            name='Qty [pcs]',
            yaxis='y1',
            marker_color='brown',
            offsetgroup=0
        ))

        # Bar Amount
        fig1.add_trace(go.Bar(
            x=monthly_summary['Month-Year'],
            y=monthly_summary['Total Amount'],
            name='Total Amount [IDR]',
            yaxis='y2',
            marker_color='grey',
            offsetgroup=1
        ))

        fig1.update_layout(
            title="Chart Qty [pcs] Vs Amount [IDR] by Month-Year (Filtered)",
            xaxis=dict(
                title="Bulan-Tahun",
                categoryorder='array',
                categoryarray=monthly_summary['Month-Year'].tolist()
            ),
            yaxis=dict(
                title="Qty [pcs]",
                showgrid=False
            ),
            yaxis2=dict(
                title="Total Amount [IDR]",
                overlaying='y',
                side='right',
                showgrid=False
            ),
            barmode='group',
            hovermode='x unified',
            margin=dict(t=60, b=80),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5
            )
        )
#endregion Grafik Bar Qty dan Amount by Month-Year

        # Tampilkan grafik bar Qty dan Amount by Month-Year

        # --- 2. Grafik Bar Qty dan Amount by PIC ---
        # Group data by PIC within the filtered date range
        pic_summary = (
            filtered_df.groupby('PIC')
            .agg({'Qty': 'sum', 'Total Amount': 'sum'})
            .reset_index()
        )

        fig3 = go.Figure()

        # Bar Qty
        fig3.add_trace(go.Bar(
            x=pic_summary['PIC'],
            y=pic_summary['Qty'],
            name='Qty [pcs]',
            yaxis='y1',
            marker_color='royalblue',
            offsetgroup=0
        ))

        # Bar Amount
        fig3.add_trace(go.Bar(
            x=pic_summary['PIC'],
            y=pic_summary['Total Amount'],
            name='Total Amount [IDR]',
            yaxis='y2',
            marker_color='seagreen',
            offsetgroup=1
        ))

        fig3.update_layout(
            title="Chart Qty [pcs] Vs Amount [IDR] by PIC (Filtered)",
            xaxis=dict(
            title="PIC",
            categoryorder='total descending'
            ),
            yaxis=dict(
            title="Qty [pcs]",
            showgrid=False
            ),
            yaxis2=dict(
            title="Total Amount [IDR]",
            overlaying='y',
            side='right',
            showgrid=False
            ),
            barmode='group',
            hovermode='x unified',
            margin=dict(t=60, b=80),
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
            )
        )

        st.plotly_chart(fig3, use_container_width=True)

        # --- 3. Grafik Pie Chart by M/C No. ---
        # Buat pie chart untuk Total Amount by M/C No.
        if not filtered_df.empty:

            # Group by M/C dan jumlah Total Amount
            pie_data = (
            filtered_df.groupby('M/C No.')['Total Amount']
            .sum()
            .reset_index()
            .sort_values('Total Amount', ascending=False)
            )

            # Buat Pie Chart
            pie_fig = go.Figure(data=[go.Pie(
            labels=pie_data['M/C No.'],
            values=pie_data['Total Amount'],
            hole=0.3,  # donut style
            hoverinfo='label+percent+value',
            textinfo='label+percent'
            )])

            pie_fig.update_layout(
            title_text="Distribution of Total Amount by M/C No. (Pie Chart)",
            margin=dict(t=60, b=40)
            )

        # --- Tampilkan 2 grafik dalam 2 kolom ---
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.plotly_chart(pie_fig, use_container_width=True)


    except ValueError:
        st.error("❌ Sheet 'USAGE' tidak ditemukan.")
    except Exception as e:
        st.error(f"⚠️ Gagal membaca file: {e}")

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="MADAM13 | Hệ Thống Tra Cứu Công Thức Pha Chế", layout="wide")

# Đường dẫn thư mục và file Excel
THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(THU_MUC_GOC, "du_lieu.xlsx")

# 🔐 Cấu hình Tài khoản và Mật khẩu tổng để truy cập trang web
USER_DANG_NHAP = "v13"
MAT_KHAU_DANG_NHAP = "050212"

# Quản lý trạng thái đăng nhập trong session_state
if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

# Quản lý luồng màn hình cảm ứng
if "man_hinh" not in st.session_state:
    st.session_state.man_hinh = "chon_nhom" # chon_nhom, chon_mon, che_do_pha_che
if "nhom_dang_chon" not in st.session_state:
    st.session_state.nhom_dang_chon = None
if "danh_sach_chon" not in st.session_state:
    st.session_state.danh_sach_chon = [] # Lưu các món được chọn pha chế
if "mon_dang_xem" not in st.session_state:
    st.session_state.mon_dang_xem = None

# ----------------- GIAO DIỆN ĐĂNG NHẬP -----------------
if not st.session_state.da_dang_nhap:
    st.title("🔒 Đăng Nhập Hệ Thống Pha Chế")
    st.markdown("Vui lòng nhập thông tin tài khoản để truy cập.")
    
    with st.form("form_dang_nhap"):
        input_user = st.text_input("Tên đăng nhập:")
        input_pass = st.text_input("Mật khẩu:", type="password")
        submit_btn = st.form_submit_button("Đăng nhập", type="primary", use_container_width=True)
        
        if submit_btn:
            if input_user == USER_DANG_NHAP and input_pass == MAT_KHAU_DANG_NHAP:
                st.session_state.da_dang_nhap = True
                st.success("🎉 Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("❌ Sai tên đăng nhập hoặc mật khẩu!")
    st.stop()

# ----------------- HÀM TẢI DỮ LIỆU & XỬ LÝ -----------------
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(EXCEL_PATH)
        df.columns = df.columns.str.strip()
        for col in ["Tên món", "Nhóm", "Công thức", "Tên file ảnh"]:
            if col not in df.columns:
                df[col] = ""
        df["Tên món"] = df["Tên món"].astype(str).replace('nan', '')
        df["Nhóm"] = df["Nhóm"].astype(str).replace('nan', '')
        return df
    except Exception as e:
        st.error(f"Lỗi khi đọc file Excel: {e}")
        return pd.DataFrame({"Tên món": [], "Nhóm": [], "Công thức": [], "Tên file ảnh": []})

df = load_data()

# ----------------- THANH ĐIỀU HƯỚNG & QUẢN TRỊ TRÊN CÙNG (TOP HEADER) -----------------
c_user, c_home, c_list, c_add, c_out = st.columns([1.5, 1.2, 1.5, 1.2, 1])

with c_user:
    st.markdown(f"👤 **{USER_DANG_NHAP}**")

with c_home:
    if st.button("🏠 Chọn nhóm", use_container_width=True):
        st.session_state.man_hinh = "chon_nhom"
        st.session_state.nhom_dang_chon = None
        st.rerun()

with c_list:
    so_luong_dang_chon = len(st.session_state.danh_sach_chon)
    btn_list_type = "primary" if so_luong_dang_chon > 0 else "secondary"
    if st.button(f"📋 Đã chọn ({so_luong_dang_chon})", use_container_width=True, type=btn_list_type):
        if so_luong_dang_chon > 0:
            st.session_state.man_hinh = "che_do_pha_che"
            st.session_state.mon_dang_xem = st.session_state.danh_sach_chon[0]
            st.rerun()
        else:
            st.warning("⚠️ Chưa có món nào được chọn!")

with c_add:
    if st.button("➕ Thêm món", use_container_width=True):
        st.session_state.mo_dialog_them = True

with c_out:
    if st.button("🚪 Thoát", use_container_width=True):
        st.session_state.da_dang_nhap = False
        st.rerun()

st.divider()

# ----------------- POPUP THÊM MÓN MỚI -----------------
@st.dialog("➕ Thêm công thức món mới", width="large")
def dialog_them_mon():
    danh_sach_nhom_hien_tai = [n for n in df["Nhóm"].unique() if str(n).strip() != ""]
    ten_mon = st.text_input("Tên món:")
    
    nhom_chon_lua = ["Chọn nhóm có sẵn", "➕ Tạo nhóm mới..."]
    lua_chon_nhom = st.radio("Phân loại nhóm:", nhom_chon_lua, horizontal=True)
    
    if lua_chon_nhom == "Chọn nhóm có sẵn":
        nhom = st.selectbox("Chọn nhóm:", danh_sach_nhom_hien_tai if danh_sach_nhom_hien_tai else ["Chung"])
    else:
        nhom = st.text_input("Nhập tên nhóm mới:")
        
    st.markdown("---")
    cong_thuc = st.text_area("Nội dung công thức chi tiết (Hỗ trợ Markdown):", height=180)
    file_anh = st.file_uploader("Chọn hình ảnh minh họa:", type=["jpg", "jpeg", "png"])
    
    if st.button("💾 Lưu món mới", type="primary", use_container_width=True):
        nhom_final = nhom.strip() if lua_chon_nhom == "➕ Tạo nhóm mới..." else nhom
        if not ten_mon.strip():
            st.warning("⚠️ Vui lòng nhập tên món!")
        else:
            ten_file_anh = ""
            if file_anh is not None:
                ten_file_anh = file_anh.name
                duong_dan_luu = os.path.join(THU_MUC_GOC, ten_file_anh)
                with open(duong_dan_luu, "wb") as f:
                    f.write(file_anh.getbuffer())
            
            try:
                df_goc = pd.read_excel(EXCEL_PATH)
            except:
                df_goc = pd.DataFrame(columns=["Tên món", "Nhóm", "Công thức", "Tên file ảnh"])
            
            dong_moi = pd.DataFrame([{"Tên món": ten_mon.strip(), "Nhóm": nhom_final.strip(), "Công thức": cong_thuc, "Tên file ảnh": ten_file_anh}])
            df_moi = pd.concat([df_goc, dong_moi], ignore_index=True)
            df_moi.to_excel(EXCEL_PATH, index=False)
            
            st.success("🎉 Đã thêm món mới thành công!")
            st.cache_data.clear()
            st.rerun()

if st.session_state.get("mo_dialog_them", False):
    st.session_state.mo_dialog_them = False
    dialog_them_mon()


# =========================================================================
# LUỒNG 1: MÀN HÌNH CHỌN NHÓM (TRANG CHỦ)
# =========================================================================
if st.session_state.man_hinh == "chon_nhom":
    st.title("🍹 HỆ THỐNG PHA CHẾ - CHỌN NHÓM MÓN")
    st.markdown("### Vui lòng chọn một nhóm thức uống để tiếp tục:")
    
    danh_sach_nhom = [n for n in df["Nhóm"].unique() if str(n).strip() != ""]
    
    if not danh_sach_nhom:
        st.warning("⚠️ Chưa có nhóm món nào trong hệ thống. Vui lòng bấm nút 'Thêm món' ở phía trên.")
    else:
        # Hiển thị các nhóm dạng các nút bấm lớn, tối ưu màn hình cảm ứng (mở rộng rộng hơn do bỏ sidebar)
        cols = st.columns(3, gap="medium")
        for i, nhom in enumerate(danh_sach_nhom):
            with cols[i % 3]:
                so_luong_mon = len(df[df["Nhóm"] == nhom])
                if st.button(f"📁 {nhom}\n\n({so_luong_mon} món)", use_container_width=True, key=f"btn_nhom_{i}HP"):
                    st.session_state.nhom_dang_chon = nhom
                    st.session_state.man_hinh = "chon_mon"
                    st.rerun()


# =========================================================================
# LUỒNG 2: MÀN HÌNH CHỌN MÓN TRONG NHÓM & TẠO DANH SÁCH PHA CHẾ
# =========================================================================
elif st.session_state.man_hinh == "chon_mon":
    nhom_hien_tai = st.session_state.nhom_dang_chon
    st.title(f"📂 Nhóm: {nhom_hien_tai}")
    
    col_back, col_title_action = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Quay lại chọn nhóm", use_container_width=True):
            st.session_state.man_hinh = "chon_nhom"
            st.session_state.nhom_dang_chon = None
            st.rerun()
            
    st.markdown("---")
    st.markdown("💡 **Chạm/Click chọn các món cần pha chế**, sau đó bấm nút **'Bắt đầu pha chế'** ở bên dưới:")

    df_nhom = df[df["Nhóm"] == nhom_hien_tai]
    danh_sach_tam = st.session_state.danh_sach_chon
    
    for idx, row in df_nhom.iterrows():
        ten_mon = row["Tên món"]
        da_chon = ten_mon in danh_sach_tam
        
        c_check, c_name, c_btn = st.columns([0.5, 4, 1.5])
        with c_check:
            is_checked = st.checkbox("Chọn", value=da_chon, key=f"chk_mon_{idx}", label_visibility="collapsed")
            if is_checked and ten_mon not in danh_sach_tam:
                st.session_state.danh_sach_chon.append(ten_mon)
            elif not is_checked and ten_mon in danh_sach_tam:
                st.session_state.danh_sach_chon.remove(ten_mon)
        with c_name:
            st.markdown(f"#### {ten_mon}")
        with c_btn:
            if st.button("🔍 Xem nhanh", key=f"xem_nhanh_{idx}", use_container_width=True):
                st.session_state.mon_xem_nhanh = row
                st.rerun()
        st.divider()

    if st.session_state.danh_sach_chon:
        st.markdown("")
        if st.button(f"🚀 BẮT ĐẦU PHA CHẾ ({len(st.session_state.danh_sach_chon)} món đã chọn)", type="primary", use_container_width=True):
            st.session_state.man_hinh = "che_do_pha_che"
            st.session_state.mon_dang_xem = st.session_state.danh_sach_chon[0]
            st.rerun()

    if "mon_xem_nhanh" in st.session_state:
        r = st.session_state.mon_xem_nhanh
        @st.dialog(f"📖 Công thức: {r['Tên món']}", width="large")
        def dialog_xem_nhanh():
            img = str(r.get("Tên file ảnh", "")).strip()
            if img and img.lower() != 'nan':
                path_img = os.path.join(THU_MUC_GOC, img)
                if os.path.exists(path_img):
                    st.image(path_img, width=300)
            st.markdown(str(r.get("Công thức", "")))
            if st.button("Đóng", use_container_width=True):
                del st.session_state.mon_xem_nhanh
                st.rerun()
        dialog_xem_nhanh()


# =========================================================================
# LUỒNG 3: MÀN HÌNH CHUYÊN DỤNG PHA CHẾ (CỘT TRÁI: DANH SÁCH ĐÃ CHỌN - CỘT PHẢI: CHI TIẾT)
# =========================================================================
elif st.session_state.man_hinh == "che_do_pha_che":
    st.title("☕ MÀN HÌNH PHA CHẾ TRỰC QUAN")
    
    danh_sach_chon = st.session_state.danh_sach_chon
    
    if not danh_sach_chon:
        st.warning("⚠️ Bạn chưa chọn món nào. Vui lòng quay lại chọn nhóm và chọn món.")
        if st.button("⬅️ Quay về chọn nhóm"):
            st.session_state.man_hinh = "chon_nhom"
            st.rerun()
    else:
        # Bố cục 2 cột tận dụng tối đa chiều rộng màn hình
        col_trai, col_phai = st.columns([1.2, 3], gap="large")
        
        with col_trai:
            st.markdown("### 📋 Danh sách món đã chọn")
            st.markdown("*(Chạm vào tên món để xem chi tiết)*")
            st.divider()
            
            for mon in danh_sach_chon:
                is_active = (st.session_state.mon_dang_xem == mon)
                btn_type = "primary" if is_active else "secondary"
                
                if st.button(f"🍹 {mon}", key=f"btn_lua_chon_{mon}", use_container_width=True, type=btn_type):
                    st.session_state.mon_dang_xem = mon
                    st.rerun()
            
            st.divider()
            if st.button("➕ Chọn thêm nhóm/món khác", use_container_width=True):
                st.session_state.man_hinh = "chon_nhom"
                st.rerun()
                
            if st.button("🗑️ Xóa sạch danh sách", use_container_width=True):
                st.session_state.danh_sach_chon = []
                st.session_state.man_hinh = "chon_nhom"
                st.rerun()

        with col_phai:
            mon_hien_tai = st.session_state.get("mon_dang_xem", danh_sach_chon[0])
            row_info = df[df["Tên món"] == mon_hien_tai]
            
            if not row_info.empty:
                r = row_info.iloc[0]
                st.markdown(f"## ✨ {mon_hien_tai}")
                st.caption(f"Nhóm: {r['Nhóm']}")
                st.divider()
                
                img_name_raw = r.get("Tên file ảnh", "")
                img_name = str(img_name_raw).strip() if not pd.isna(img_name_raw) else ""
                if img_name and img_name.lower() != 'nan':
                    duong_dan_hien_thi = os.path.join(THU_MUC_GOC, img_name)
                    if os.path.exists(duong_dan_hien_thi):
                        st.image(duong_dan_hien_thi, width=350)
                
                cong_thuc_ct = str(r.get("Công thức", ""))
                st.markdown(cong_thuc_ct, unsafe_allow_html=True)
            else:
                st.warning("Không tìm thấy thông tin chi tiết của món này.")

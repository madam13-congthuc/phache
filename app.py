import streamlit as st
import pandas as pd
import io
import unicodedata
import os

st.set_page_config(page_title="MD13 | Quản Lý Công Thức", layout="wide")

# Đường dẫn thư mục và file Excel
THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(THU_MUC_GOC, "du_lieu.xlsx")

# 🔐 Cấu hình Tài khoản và Mật khẩu tổng để truy cập trang web
# Bạn có thể thay đổi tùy ý tên đăng nhập và mật khẩu ở đây
USER_DANG_NHAP = "admin"
MAT_KHAU_DANG_NHAP = "123456"

# Quản lý trạng thái đăng nhập trong session_state
if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

# ----------------- GIAO DIỆN ĐĂNG NHẬP (NẾU CHƯA ĐĂNG NHẬP) -----------------
if not st.session_state.da_dang_nhap:
    st.title("🔒 Đăng Nhập Hệ Thống")
    st.markdown("Vui lòng nhập thông tin tài khoản để truy cập vào ứng dụng quản lý công thức.")
    
    with st.form("form_dang_nhap"):
        input_user = st.text_input("Tên đăng nhập:")
        input_pass = st.text_input("Mật khẩu:", type="password")
        submit_btn = st.form_submit_button("Đăng nhập", type="primary", use_container_width=True)
        
        if submit_btn:
            if input_user == USER_DANG_NHAP and input_pass == MAT_KHAU_DANG_NHAP:
                st.session_state.da_dang_nhap = True
                st.success("🎉 Đăng nhập thành công! Đang tải ứng dụng...")
                st.rerun()
            else:
                st.error("❌ Tên đăng nhập hoặc mật khẩu không chính xác!")
                
    st.stop( )  # Dừng lại ở đây, không cho hiển thị phần code bên dưới nếu chưa đăng nhập


# ----------------- GIAO DIỆN CHÍNH CỦA ỨNG DỤNG (SAU KHI ĐÃ ĐĂNG NHẬP) -----------------
st.title("🍹 MADAM13 | Công Thức Pha Chế")

# Nút đăng xuất ở góc trên thanh Sidebar hoặc màn hình chính
with st.sidebar:
    st.write(f"👤 Đang đăng nhập: **{USER_DANG_NHAP}**")
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.da_dang_nhap = False
        st.rerun()

# 1. Hàm chuẩn hóa tiếng Việt
def xu_ly_chu(text):
    if pd.isna(text) or text is None:
        return ""
    text = str(text).strip().lower()
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    text = text.replace('đ', 'd')
    return text

# 2. Hàm tải dữ liệu an toàn
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
        st.error(f"Lỗi khi đọc file Excel tại đường dẫn `{EXCEL_PATH}`: {e}")
        return pd.DataFrame({"Tên món": [], "Nhóm": [], "Công thức": [], "Tên file ảnh": []})

df = load_data()

# 3. Hàm Popup Thêm món mới
@st.dialog("➕ Thêm công thức món mới", width="large")
def dialog_them_mon(danh_sach_nhom_hien_tai):
    ten_mon = st.text_input("Tên món:", key="add_ten_mon")
    
    nhom_chon_lua = ["Chọn nhóm có sẵn", "➕ Tạo nhóm mới..."]
    lua_chon_nhom = st.radio("Phân loại nhóm:", nhom_chon_lua, horizontal=True, key="add_radio_nhom")
    
    if lua_chon_nhom == "Chọn nhóm có sẵn":
        danh_sach_hop_le = [n for n in danh_sach_nhom_hien_tai if n != "Tất cả"]
        nhom = st.selectbox("Chọn nhóm:", danh_sach_hop_le, key="add_select_nhom")
    else:
        nhom = st.text_input("Nhập tên nhóm mới vào đây:", key="add_input_nhom_moi")
        
    st.markdown("---")
    
    if "input_cong_thuc" not in st.session_state:
        st.session_state.input_cong_thuc = ""

    cong_thuc = st.text_area(
        "Nội dung công thức chi tiết (Hỗ trợ định dạng Markdown):", 
        value=st.session_state.input_cong_thuc,
        height=180,
        key="add_text_area_ct"
    )
    st.session_state.input_cong_thuc = cong_thuc

    file_anh = st.file_uploader("Chọn hình ảnh minh họa từ máy:", type=["jpg", "jpeg", "png"], key="add_file_up")
    
    if st.button("💾 Lưu món mới", type="primary", use_container_width=True, key="add_btn_save"):
        nhom_final = nhom.strip() if lua_chon_nhom == "➕ Tạo nhóm mới..." else nhom
        if not ten_mon.strip():
            st.warning("⚠️ Vui lòng nhập tên món trước khi lưu!")
        elif not nhom_final:
            st.warning("⚠️ Vui lòng chọn hoặc nhập tên nhóm!")
        else:
            ten_file_anh = ""
            if file_anh is not None:
                ten_file_anh = file_anh.name
                duong_dan_luu_anh = os.path.join(THU_MUC_GOC, ten_file_anh)
                with open(duong_dan_luu_anh, "wb") as f:
                    f.write(file_anh.getbuffer())
            
            try:
                df_hien_tai = pd.read_excel(EXCEL_PATH)
            except:
                df_hien_tai = pd.DataFrame(columns=["Tên món", "Nhóm", "Công thức", "Tên file ảnh"])
            
            dong_moi = pd.DataFrame([{
                "Tên món": ten_mon.strip(),
                "Nhóm": nhom_final.strip(),
                "Công thức": cong_thuc,
                "Tên file ảnh": ten_file_anh
            }])
            
            df_moi = pd.concat([df_hien_tai, dong_moi], ignore_index=True)
            df_moi.to_excel(EXCEL_PATH, index=False)
            
            st.session_state.input_cong_thuc = ""
            st.success("🎉 Đã thêm món mới thành công!")
            st.balloons()
            
            st.cache_data.clear()
            st.rerun()

# 4. Hàm Popup Chỉnh sửa món
@st.dialog("✏️ Chỉnh sửa thông tin món", width="large")
def dialog_sua_mon(index_dong, row_data, danh_sach_nhom_hien_tai):
    ten_mon_cu = row_data["Tên món"]
    nhom_cu = row_data["Nhóm"]
    cong_thuc_cu = row_data["Công thức"]
    anh_cu = row_data["Tên file ảnh"]

    ten_mon_moi = st.text_input("Tên món:", value=str(ten_mon_cu), key=f"edit_ten_{index_dong}")
    
    danh_sach_hop_le = [n for n in danh_sach_nhom_hien_tai if n != "Tất cả"]
    try:
        vi_tri_nhom_cu = danh_sach_hop_le.index(nhom_cu) if nhom_cu in danh_sach_hop_le else 0
    except:
        vi_tri_nhom_cu = 0
        
    nhom_chon_lua = ["Chọn nhóm có sẵn", "➕ Tạo nhóm mới..."]
    lua_chon_nhom = st.radio("Phân loại nhóm:", nhom_chon_lua, horizontal=True, key=f"edit_radio_{index_dong}")
    
    if lua_chon_nhom == "Chọn nhóm có sẵn":
        nhom_moi = st.selectbox("Chọn nhóm:", danh_sach_hop_le, index=vi_tri_nhom_cu, key=f"edit_select_{index_dong}")
    else:
        nhom_moi = st.text_input("Nhập tên nhóm mới vào đây:", key=f"edit_input_nhom_{index_dong}")
        
    st.markdown("---")
    st.markdown(f"🖼️ **Ảnh hiện tại:** `{anh_cu if pd.notna(anh_cu) and str(anh_cu).strip() != '' else 'Không có'}`")
    file_anh_moi = st.file_uploader("Chọn ảnh mới (nếu muốn thay thế ảnh cũ):", type=["jpg", "jpeg", "png"], key=f"edit_file_{index_dong}")

    cong_thuc_moi = st.text_area(
        "Nội dung công thức chi tiết:", 
        value=str(cong_thuc_cu) if pd.notna(cong_thuc_cu) else "",
        height=200,
        key=f"edit_ta_{index_dong}"
    )

    if st.button("💾 Cập nhật thay đổi", type="primary", use_container_width=True, key=f"edit_btn_save_{index_dong}"):
        nhom_final = nhom_moi.strip() if lua_chon_nhom == "➕ Tạo nhóm mới..." else nhom_moi
        if not ten_mon_moi.strip():
            st.warning("⚠️ Tên món không được để trống!")
        else:
            ten_file_anh_final = anh_cu
            if file_anh_moi is not None:
                ten_file_anh_final = file_anh_moi.name
                duong_dan_luu_anh = os.path.join(THU_MUC_GOC, ten_file_anh_final)
                with open(duong_dan_luu_anh, "wb") as f:
                    f.write(file_anh_moi.getbuffer())

            try:
                df_goc = pd.read_excel(EXCEL_PATH)
                df_goc.loc[index_dong, "Tên món"] = ten_mon_moi.strip()
                df_goc.loc[index_dong, "Nhóm"] = nhom_final.strip()
                df_goc.loc[index_dong, "Công thức"] = cong_thuc_moi
                df_goc.loc[index_dong, "Tên file ảnh"] = ten_file_anh_final
                
                df_goc.to_excel(EXCEL_PATH, index=False)
                
                st.success("✨ Cập nhật món thành công!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi lưu cập nhật: {e}")

# 5. Hàm Popup Xóa món (Có xác nhận)
@st.dialog("🗑️ Xác nhận xóa món", width="medium")
def dialog_xoa_mon(index_dong, row_data):
    st.error(f"⚠️ Bạn đang chuẩn bị xóa món: **{row_data['Tên món']}**")
    xac_nhan_checkbox = st.checkbox("Tôi chắc chắn muốn xóa vĩnh viễn món này", key=f"cb_del_{index_dong}")

    if st.button("🗑️ Đồng ý Xóa", type="primary", use_container_width=True, key=f"btn_confirm_del_{index_dong}"):
        if not xac_nhan_checkbox:
            st.warning("⚠️ Vui lòng tích chọn xác nhận muốn xóa!")
        else:
            try:
                df_goc = pd.read_excel(EXCEL_PATH)
                df_goc = df_goc.drop(index_dong).reset_index(drop=True)
                df_goc.to_excel(EXCEL_PATH, index=False)
                
                st.success("🗑️ Đã xóa món thành công khỏi hệ thống!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi xóa dữ liệu: {e}")

# 6. Khu vực tìm kiếm, bộ lọc và nút Thêm món
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    tim_kiem = st.text_input("🔍 Nhập tên món để tìm kiếm nhanh:")
with col2:
    danh_sach_nhom = ["Tất cả"] + [n for n in df["Nhóm"].unique() if str(n).strip() != ""]
    nhom_chon = st.selectbox("📂 Lọc theo nhóm:", danh_sach_nhom)
with col3:
    st.write("") 
    st.write("") 
    if st.button("➕ Thêm món mới", use_container_width=True):
        dialog_them_mon(danh_sach_nhom)

# 7. Lọc dữ liệu thông minh
df_loc = df.copy()

if tim_kiem:
    tu_khoa = xu_ly_chu(tim_kiem)
    df_loc['Ten_mon_chuan'] = df_loc['Tên món'].apply(xu_ly_chu)
    df_loc = df_loc[df_loc['Ten_mon_chuan'].astype(str).str.contains(tu_khoa, case=False, na=False)]

if nhom_chon != "Tất cả":
    df_loc = df_loc[df_loc["Nhóm"] == nhom_chon]

# 8. Hiển thị kết quả kèm nút Chỉnh sửa và Xóa
st.divider()
if df_loc.empty:
    st.warning("⚠️ Không tìm thấy món nào phù hợp. Vui lòng thử từ khóa khác.")
else:
    for idx, row in df_loc.iterrows():
        c1, c2 = st.columns([1, 3])
        with c1:
            img_name_raw = row.get("Tên file ảnh", "")
            img_name = str(img_name_raw).strip() if not pd.isna(img_name_raw) else ""

            if img_name and img_name.lower() != 'nan':
                duong_dan_hien_thi = os.path.join(THU_MUC_GOC, img_name)
                if os.path.exists(duong_dan_hien_thi):
                    st.image(duong_dan_hien_thi, width=250)
                else:
                    st.error(f"🚫 Thiếu file: {img_name}")
            else:
                st.info("🖼️ Chưa có ảnh")
        with c2:
            col_tieu_de, col_sua, col_xoa = st.columns([3, 1, 1])
            with col_tieu_de:
                st.subheader(row["Tên món"])
                st.caption(f"Nhóm: {row['Nhóm']}")
            with col_sua:
                if st.button("✏️ Sửa", key=f"main_edit_btn_{idx}", use_container_width=True):
                    dialog_sua_mon(idx, row, danh_sach_nhom)
            with col_xoa:
                if st.button("🗑️ Xóa", key=f"main_del_btn_{idx}", use_container_width=True):
                    dialog_xoa_mon(idx, row)
            
            cong_thuc = str(row.get("Công thức", ""))
            st.markdown(cong_thuc, unsafe_allow_html=True)
            
        st.divider()

# 9. Chức năng xuất file
st.subheader("📥 Xuất và In ấn")
st.write("Nhấn `Ctrl + P` trên trình duyệt để in hoặc lưu thành PDF. Tải file Excel danh sách hiện tại bên dưới:")

buffer = io.BytesIO()
df_xuat = df_loc[["Tên món", "Nhóm", "Công thức", "Tên file ảnh"]]
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df_xuat.to_excel(writer, index=False)
    
st.download_button(
    label="Tải danh sách ra Excel",
    data=buffer,
    file_name="ket_qua_tim_kiem.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

import streamlit as st
import tabula
import pandas as pd
import os
import time
import subprocess
import PyPDF2  # PDF 텍스트 추출을 위한 라이브러리 추가

# 페이지 설정
st.set_page_config(
    page_title="PDF Analyzer",
    page_icon="📊",
    layout="wide"
)

def process_pdf(file_path, start_page, end_page, lattice, stream, guess):
    try:
        pages = f"{start_page}-{end_page}"
        st.write(f"PDF 처리 시작: {file_path}")
        st.write(f"페이지 범위: {pages}")
        st.write(f"옵션: lattice={lattice}, stream={stream}, guess={guess}")
        
        # Java 버전 확인
        java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
        st.write(f"Java 버전: {java_version.decode()}")
        
        # 페이지별로 다른 옵션 시도
        all_tables = []
        for page in range(start_page, end_page + 1):
            st.write(f"\n페이지 {page} 처리 중...")
            
            try:
                # 첫 번째 시도: 기본 옵션
                tables = tabula.read_pdf(
                    file_path,
                    pages=str(page),
                    multiple_tables=True,
                    lattice=lattice,
                    stream=stream,
                    guess=guess,
                    pandas_options={'header': 0},
                    java_options=['-Dfile.encoding=UTF8', '-Xmx4g']  # 메모리 제한 증가
                )
                
                # 표를 찾지 못한 경우 다른 옵션으로 시도
                if not tables or all(df.empty for df in tables):
                    st.write(f"페이지 {page}에서 표를 찾지 못했습니다. 다른 옵션으로 시도합니다...")
                    
                    # 두 번째 시도: lattice와 stream 옵션 반전
                    tables = tabula.read_pdf(
                        file_path,
                        pages=str(page),
                        multiple_tables=True,
                        lattice=not lattice,
                        stream=not stream,
                        guess=guess,
                        pandas_options={'header': 0},
                        java_options=['-Dfile.encoding=UTF8', '-Xmx4g']
                    )
                
                # 여전히 표를 찾지 못한 경우
                if not tables or all(df.empty for df in tables):
                    st.write(f"페이지 {page}에서 표를 찾지 못했습니다. 마지막 옵션으로 시도합니다...")
                    
                    # 마지막 시도: guess 비활성화
                    tables = tabula.read_pdf(
                        file_path,
                        pages=str(page),
                        multiple_tables=True,
                        lattice=lattice,
                        stream=stream,
                        guess=False,
                        pandas_options={'header': 0},
                        java_options=['-Dfile.encoding=UTF8', '-Xmx4g']
                    )
                
                if tables and any(not df.empty for df in tables):
                    all_tables.extend(tables)
                    st.write(f"페이지 {page}에서 {len(tables)}개의 표를 찾았습니다.")
                else:
                    st.warning(f"페이지 {page}에서 표를 찾지 못했습니다.")
                    
            except Exception as e:
                st.error(f"페이지 {page} 처리 중 오류 발생: {str(e)}")
                continue
        
        if not all_tables:
            st.warning("선택한 페이지 범위에서 표를 찾을 수 없습니다.")
            return None
            
        return all_tables
    except Exception as e:
        st.error(f"PDF 처리 중 오류 발생: {str(e)}")
        st.error("다음 사항을 확인해주세요:")
        st.error("1. PDF 파일이 손상되지 않았는지 확인")
        st.error("2. Java가 올바르게 설치되어 있는지 확인")
        st.error("3. 다른 추출 옵션을 시도해보세요")
        return None

def extract_text_and_tables(pdf_path, start_page, end_page):
    try:
        text_content = []
        tables_content = []
        
        # 텍스트 추출
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(start_page - 1, end_page):
                if page_num < len(pdf_reader.pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    text_content.append(f"=== 페이지 {page_num + 1} ===\n{text}\n")
        
        # 표 추출
        for page in range(start_page, end_page + 1):
            st.write(f"\n페이지 {page}의 표 추출 중...")
            
            # lattice 모드로 시도
            tables = tabula.read_pdf(
                pdf_path,
                pages=str(page),
                multiple_tables=True,
                lattice=True,
                stream=False,
                guess=True,
                pandas_options={'header': 0},
                java_options=['-Dfile.encoding=UTF8', '-Xmx4g']
            )
            
            # 표를 찾지 못한 경우 stream 모드로 시도
            if not tables or all(df.empty for df in tables):
                tables = tabula.read_pdf(
                    pdf_path,
                    pages=str(page),
                    multiple_tables=True,
                    lattice=False,
                    stream=True,
                    guess=True,
                    pandas_options={'header': 0},
                    java_options=['-Dfile.encoding=UTF8', '-Xmx4g']
                )
            
            if tables and any(not df.empty for df in tables):
                tables_content.append((page, tables))
        
        return text_content, tables_content
    except Exception as e:
        st.error(f"내용 추출 중 오류 발생: {str(e)}")
        return None, None

st.title("📊 PDF Analyzer")
st.markdown("PDF 파일에서 표를 추출하여 Excel 파일로 변환합니다.")

# 파일 경로 입력
pdf_path = st.text_input(
    "PDF 파일의 전체 경로를 입력하세요",
    value=st.session_state.get('pdf_path', ''),
    help="PDF 파일의 전체 경로를 입력하세요. 예: /home/ubuntu/documents/example.pdf"
)

if pdf_path and os.path.exists(pdf_path):
    if pdf_path.lower().endswith('.pdf'):
        # 파일 정보 표시
        file_size = os.path.getsize(pdf_path) / 1024  # KB
        file_details = {
            "파일명": os.path.basename(pdf_path),
            "파일크기": f"{file_size:.2f} KB",
            "파일경로": pdf_path
        }
        st.write(file_details)

        # 페이지 범위 입력
        col1, col2 = st.columns(2)
        with col1:
            start_page = st.number_input("시작 페이지", min_value=1, value=1)
        with col2:
            end_page = st.number_input("끝 페이지", min_value=1, value=1)

        # 추출 옵션
        with st.expander("추출 옵션"):
            lattice = st.checkbox("격자형 표 사용", value=True, help="표에 선이 있는 경우 선택")
            stream = st.checkbox("스트림 모드 사용", value=False, help="표에 선이 없는 경우 선택")
            guess = st.checkbox("표 위치 자동 감지", value=True, help="표 위치를 자동으로 감지")

        # 버튼을 중앙에 배치하고 크기 조정
        col1, col2, col3 = st.columns([1, 2, 1])  # 중앙 정렬을 위한 3개 컬럼
        with col2:
            st.markdown("""
                <style>
                div[data-testid="stButton"] {
                    width: 25%;
                    margin: 0 auto;
                }
                </style>
            """, unsafe_allow_html=True)
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                extract_info = st.button("현장정보 추출", type="primary")
            with col_btn2:
                extract_tables = st.button("표 추출하기", type="primary")

        if extract_info:
            try:
                with st.spinner("현장정보 추출 중..."):
                    # 페이지 범위 설정
                    info_start_page = start_page if start_page > 0 else 1
                    info_end_page = end_page if end_page > 0 else 5
                    
                    # 1-5 페이지 텍스트와 표 추출
                    text_content, tables_content = extract_text_and_tables(pdf_path, info_start_page, info_end_page)
                    
                    if text_content or tables_content:
                        # PDF 파일명 가져오기 (확장자 제외)
                        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
                        
                        # 텍스트 내용 표시
                        if text_content:
                            st.subheader(f"추출된 텍스트 (페이지 {info_start_page}-{info_end_page})")
                            st.text_area("텍스트 내용", "\n".join(text_content), height=400)
                        
                        # 표 내용 표시
                        if tables_content:
                            st.subheader(f"추출된 표 (페이지 {info_start_page}-{info_end_page})")
                            for page, tables in tables_content:
                                st.write(f"=== 페이지 {page}의 표 ===")
                                for i, df in enumerate(tables):
                                    if not df.empty:
                                        st.write(f"표 {i+1}")
                                        st.dataframe(df)
                        
                        # 텍스트 파일로 다운로드
                        text_file_path = os.path.join("temp", f"{pdf_filename}_text.txt")
                        os.makedirs("temp", exist_ok=True)
                        
                        with open(text_file_path, "w", encoding="utf-8") as f:
                            f.write("\n".join(text_content))
                        
                        with open(text_file_path, "r", encoding="utf-8") as f:
                            st.download_button(
                                label="텍스트 파일 다운로드",
                                data=f,
                                file_name=f"{pdf_filename}_text.txt",
                                mime="text/plain"
                            )
                        
                        # Excel 파일로 다운로드 (표만)
                        if tables_content:
                            excel_path = os.path.join("temp", f"{pdf_filename}_tables.xlsx")
                            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                                for page, tables in tables_content:
                                    for i, df in enumerate(tables):
                                        if not df.empty:
                                            sheet_name = f'Page{page}_Table{i+1}'
                                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                            with open(excel_path, 'rb') as f:
                                st.download_button(
                                    label="표 Excel 파일 다운로드",
                                    data=f,
                                    file_name=f"{pdf_filename}_tables.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        
                            # 임시 Excel 파일 정리
                            if os.path.exists(excel_path):
                                os.unlink(excel_path)
                        
                        # 임시 텍스트 파일 정리
                        if os.path.exists(text_file_path):
                            os.unlink(text_file_path)
                    else:
                        st.warning("내용을 추출할 수 없습니다.")
            except Exception as e:
                st.error(f"처리 중 오류가 발생했습니다: {str(e)}")
                st.error("다시 시도해주세요.")

        elif extract_tables:
            try:
                with st.spinner("PDF 파일 처리 중..."):
                    # PDF 처리
                    tables = process_pdf(pdf_path, start_page, end_page, lattice, stream, guess)
                    
                    if tables and any(not df.empty for df in tables):
                        # PDF 파일명 가져오기 (확장자 제외)
                        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
                        
                        # Excel 파일로 저장
                        output_path = os.path.join("temp", f"{pdf_filename}_tables.xlsx")
                        os.makedirs("temp", exist_ok=True)
                        
                        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                            for i, df in enumerate(tables):
                                if not df.empty:
                                    # 빈 컬럼도 포함하여 저장
                                    df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)

                        # 다운로드 버튼
                        with open(output_path, 'rb') as f:
                            st.download_button(
                                label="Excel 파일 다운로드",
                                data=f,
                                file_name=f"{pdf_filename}_tables.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                        # 미리보기
                        st.success("표 추출이 완료되었습니다!")
                        for i, df in enumerate(tables):
                            if not df.empty:
                                st.write(f"표 {i+1}")
                                st.dataframe(df)

                        # 임시 파일 정리
                        if os.path.exists(output_path):
                            os.unlink(output_path)
                    else:
                        st.warning("선택한 페이지 범위에서 표를 찾을 수 없습니다.")

            except Exception as e:
                st.error(f"처리 중 오류가 발생했습니다: {str(e)}")
                st.error("다시 시도해주세요.")
    else:
        st.error("PDF 파일만 지원됩니다.")
elif pdf_path:
    st.error("파일을 찾을 수 없습니다. 경로를 확인해주세요.")

# 사용 방법
with st.expander("사용 방법"):
    st.markdown("""
    1. PDF 파일의 전체 경로를 입력합니다.
       - 예: C:\\Users\\사용자명\\Documents\\example.pdf
    2. 표가 있는 페이지 범위를 입력합니다.
    3. 필요한 경우 추출 옵션을 설정합니다:
       - 격자형 표: 표에 선이 있는 경우 선택
       - 스트림 모드: 표에 선이 없는 경우 선택
       - 자동 감지: 표 위치를 자동으로 감지
    4. '표 추출하기' 버튼을 클릭합니다.
    5. 추출된 표를 Excel 파일로 다운로드합니다.
    """) 
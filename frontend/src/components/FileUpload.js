import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, AlertCircle } from 'lucide-react';
import styled from 'styled-components';

const DropzoneContainer = styled.div`
  border: 2px dashed ${props => props.$isDragActive ? '#007bff' : '#ddd'};
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  background: ${props => props.$isDragActive ? '#f8f9ff' : '#fafafa'};
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    border-color: #007bff;
    background: #f8f9ff;
  }
`;

const UploadIcon = styled.div`
  font-size: 3rem;
  color: #007bff;
  margin-bottom: 20px;
`;

const UploadText = styled.div`
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 10px;
`;

const UploadSubtext = styled.div`
  color: #666;
  font-size: 0.9rem;
`;

// Удалены неиспользуемые styled компоненты

const ErrorMessage = styled.div`
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
  border-radius: 6px;
  padding: 15px;
  margin-top: 20px;
  display: flex;
  align-items: center;
`;

const ErrorIcon = styled(AlertCircle)`
  margin-right: 10px;
  flex-shrink: 0;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const Spinner = styled.div`
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

function FileUpload({ onFileUpload, loading, acceptedFormats }) {
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      const error = rejectedFiles[0].errors[0];
      if (error.code === 'file-invalid-type') {
        alert(`Неподдерживаемый формат файла. Поддерживаются: ${acceptedFormats.join(', ')}`);
      } else {
        alert(`Ошибка: ${error.message}`);
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload, acceptedFormats]);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/epub+zip': ['.epub']
    },
    multiple: false,
    maxSize: 50 * 1024 * 1024 // 50MB
  });

  if (loading) {
    return (
      <LoadingSpinner>
        <Spinner />
        <span style={{ marginLeft: '15px' }}>Загрузка и обработка файла...</span>
      </LoadingSpinner>
    );
  }

  return (
    <div>
      <DropzoneContainer {...getRootProps()} $isDragActive={isDragActive}>
        <input {...getInputProps()} />
        <UploadIcon>
          <Upload size={48} />
        </UploadIcon>
        <UploadText>
          {isDragActive ? 'Отпустите файл здесь' : 'Перетащите файл сюда или нажмите для выбора'}
        </UploadText>
        <UploadSubtext>
          Поддерживаемые форматы: {acceptedFormats.join(', ')} (максимум 50MB)
        </UploadSubtext>
      </DropzoneContainer>

      {fileRejections.length > 0 && (
        <ErrorMessage>
          <ErrorIcon size={20} />
          <div>
            <strong>Ошибка загрузки файла:</strong>
            <ul style={{ margin: '5px 0 0 20px' }}>
              {fileRejections.map(({ file, errors }) => (
                <li key={file.name}>
                  {file.name}: {errors.map(e => e.message).join(', ')}
                </li>
              ))}
            </ul>
          </div>
        </ErrorMessage>
      )}

      <div style={{ marginTop: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '6px' }}>
        <h4 style={{ marginBottom: '10px', color: '#495057' }}>Инструкции:</h4>
        <ul style={{ color: '#6c757d', lineHeight: '1.6' }}>
          <li>Загрузите PDF, DOCX или EPUB файл вашей книги</li>
          <li>Файл будет автоматически проанализирован для определения структуры</li>
          <li>Система найдет заголовки и разделы в тексте</li>
          <li>Максимальный размер файла: 50MB</li>
        </ul>
      </div>
    </div>
  );
}

export default FileUpload;

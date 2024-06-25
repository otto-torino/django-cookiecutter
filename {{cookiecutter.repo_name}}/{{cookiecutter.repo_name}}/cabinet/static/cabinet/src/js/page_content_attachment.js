;(function () {
  document.addEventListener('DOMContentLoaded', () => {
    const typeField = document.getElementById('id_type')
    const fileFieldRow = document.querySelector('.field-file')
    const folderFieldRow = document.querySelector('.field-folder')

    const handleAttachmentTypeChange = () => {
      if (typeField.value === 'file') {
        fileFieldRow.classList.remove('d-none')
        folderFieldRow.classList.add('d-none')
      } else {
        fileFieldRow.classList.add('d-none')
        folderFieldRow.classList.remove('d-none')
      }
    }

    typeField.addEventListener('change', handleAttachmentTypeChange)
    handleAttachmentTypeChange()
  })
})()

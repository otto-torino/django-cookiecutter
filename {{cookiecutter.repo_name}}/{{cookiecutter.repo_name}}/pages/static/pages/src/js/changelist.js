;(function ($) {
  const form = document.getElementById('changelist-form')
  const pageId = form.dataset.pageId
  const savePositionUrl = form.dataset.savePositionUrl
  const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value

  // Handle the content type change
  $('#id_content_module').change(function () {
    let description = $(this).find('option:selected').data('description')
    $('#content_type_description').html(description)
  })

  // Handle the content block add
  $('#add-content-block').click(function () {
    const alertMessage = $(this).data('alert-message')
    let contentModule = $('#id_content_module').val()
    if (!contentModule) {
      alert(alertMessage)
      return
    }
    let url = $('#id_content_module').find('option:selected').data('url')
    window.location.assign(url + '?page=' + pageId)
  })

  // Handle the content block delete
  const initDelete = () => {
    const deleteForm = document.querySelector('#delete-content-block-form')
    const confirmModal = new Baton.Modal({
      title: deleteForm.dataset.modalTitle,
      content: deleteForm.dataset.modalContent,
      size: 'sm',
      actionBtnCb: () => {},
    })
    const deleteContentBlock = (action) => () => {
      deleteForm.action = action
      deleteForm.submit()
    }
    const deleteBtns = document.querySelectorAll('[data-toggle="delete-content-block"]')
    if (deleteBtns) {
      deleteBtns.forEach((btn) => {
        const contentDeleteUrl = btn.dataset.deleteUrl
        btn.addEventListener('click', (e) => {
          e.preventDefault()
          confirmModal.update({
            actionBtnLabel: deleteForm.dataset.modalButton,
            actionBtnCb: deleteContentBlock(contentDeleteUrl),
          })
          confirmModal.open()
        })
      })
    }
  }

  const buildPayload = (order) => {
    return { order: order.map((id, position) => ({ id, position })) }
  }

  const handleSavePosition = (payload) => {
    // todo: reset content blocks position on failure?
    $.ajax({
      url: savePositionUrl,
      method: 'POST',
      data: JSON.stringify(payload),
      contentType: 'application/json',
      dataType: 'json',
      headers: { 'X-CSRFToken': csrfToken },
    })
  }

  const initSortable = () => {
    const list = document.querySelector('#content-blocks-list')
    const sortable = new Sortable(list, {
      handle: '.content-block-drag-handle',
      animation: 150,
      swapThreshold: 0.65,
      easing: 'cubic-bezier(1, 0, 0, 1)',
      store: {
        /**
         * Save the order of elements. Called onEnd (when the item is dropped).
         * @param {Sortable}  sortable
         */
        set: function (sortable) {
          const order = sortable.toArray()
          const payload = buildPayload(order)
          handleSavePosition(payload)
        },
      },
    })
  }

  initDelete()
  initSortable()
})(Baton.jQuery)

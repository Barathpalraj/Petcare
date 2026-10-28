/**
 * Smart Veterinary Clinic - Billing & Invoice Generator
 * Real-time calculation of line items, tax, discounts, and total
 */

document.addEventListener('DOMContentLoaded', () => {
  const invoiceItemsTable = document.getElementById('invoiceItemsTable');
  const addItemBtn = document.getElementById('addInvoiceItemBtn');
  const subtotalEl = document.getElementById('invoiceSubtotal');
  const taxInput = document.getElementById('invoiceTaxRate');
  const taxAmountEl = document.getElementById('invoiceTaxAmount');
  const discountInput = document.getElementById('invoiceDiscount');
  const grandTotalEl = document.getElementById('invoiceGrandTotal');
  const hiddenTotalInput = document.getElementById('hiddenGrandTotal');

  if (invoiceItemsTable && addItemBtn) {
    addItemBtn.addEventListener('click', () => {
      const tbody = invoiceItemsTable.querySelector('tbody');
      const row = document.createElement('tr');
      row.className = 'invoice-row';
      row.innerHTML = `
        <td><input type="text" name="item_desc[]" class="form-control item-desc" placeholder="Service / Item Name" required></td>
        <td>
          <select name="item_type[]" class="form-control">
            <option value="consultation">Consultation</option>
            <option value="medicine">Medicine</option>
            <option value="vaccine">Vaccine</option>
            <option value="treatment">Treatment / Surgery</option>
            <option value="other">Other</option>
          </select>
        </td>
        <td><input type="number" name="item_qty[]" class="form-control item-qty" value="1" min="1" step="1" required style="width: 80px;"></td>
        <td><input type="number" name="item_price[]" class="form-control item-price" value="0.00" min="0" step="0.5" required style="width: 100px;"></td>
        <td><span class="item-line-total font-bold">₹0.00</span></td>
        <td>
          <button type="button" class="action-btn delete remove-item-btn"><i class="fas fa-trash"></i></button>
        </td>
      `;

      tbody.appendChild(row);
      attachItemEvents(row);
      recalculateTotals();

      if (typeof anime !== 'undefined') {
        anime({
          targets: row,
          backgroundColor: ['#f0fdfa', '#ffffff'],
          duration: 600,
          easing: 'easeOutQuad'
        });
      }
    });

    function attachItemEvents(row) {
      const qtyInput = row.querySelector('.item-qty');
      const priceInput = row.querySelector('.item-price');
      const deleteBtn = row.querySelector('.remove-item-btn');

      if (qtyInput) qtyInput.addEventListener('input', recalculateTotals);
      if (priceInput) priceInput.addEventListener('input', recalculateTotals);
      if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
          row.remove();
          recalculateTotals();
        });
      }
    }

    // Attach to existing rows
    const existingRows = invoiceItemsTable.querySelectorAll('tbody tr');
    existingRows.forEach(row => attachItemEvents(row));

    if (taxInput) taxInput.addEventListener('input', recalculateTotals);
    if (discountInput) discountInput.addEventListener('input', recalculateTotals);

    function recalculateTotals() {
      let subtotal = 0;
      const rows = invoiceItemsTable.querySelectorAll('tbody tr');

      rows.forEach(row => {
        const qty = parseFloat(row.querySelector('.item-qty')?.value) || 0;
        const price = parseFloat(row.querySelector('.item-price')?.value) || 0;
        const lineTotal = qty * price;
        const lineTotalSpan = row.querySelector('.item-line-total');
        if (lineTotalSpan) {
          lineTotalSpan.innerText = '₹' + lineTotal.toFixed(2);
        }
        subtotal += lineTotal;
      });

      const taxRate = parseFloat(taxInput?.value || '8') / 100;
      const taxAmount = subtotal * taxRate;
      const discount = parseFloat(discountInput?.value || '0') || 0;
      const grandTotal = Math.max(0, subtotal + taxAmount - discount);

      if (subtotalEl) subtotalEl.innerText = '₹' + subtotal.toFixed(2);
      if (taxAmountEl) taxAmountEl.innerText = '₹' + taxAmount.toFixed(2);
      if (grandTotalEl) grandTotalEl.innerText = '₹' + grandTotal.toFixed(2);
      if (hiddenTotalInput) hiddenTotalInput.value = grandTotal.toFixed(2);
    }

    recalculateTotals();
  }
});

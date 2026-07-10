function getFormData(formId) {
    const form = document.getElementById(formId);
    return form ? new FormData(form) : null;
}

function nullableValue(value) {
    return value ? String(value) : null;
}

function intValue(value, fallback = null) {
    const parsed = parseInt(value, 10);
    return Number.isFinite(parsed) ? parsed : fallback;
}

export function dateInputValue(offsetDays = 0) {
    const date = new Date();
    date.setDate(date.getDate() + offsetDays);
    return date.toISOString().split('T')[0];
}

export function buildCreateLoanPayload(formId = 'createLoanForm') {
    const formData = getFormData(formId);
    if (!formData) {
        return { isValid: false, payload: null };
    }

    const payload = {
        book_copy_id: formData.get('book_copy_id'),
        member_id: formData.get('member_id'),
        employee_id: nullableValue(formData.get('employee_id')),
        loan_date: formData.get('loan_date'),
        due_date: formData.get('due_date')
    };

    return {
        isValid: Boolean(payload.book_copy_id && payload.member_id && payload.loan_date && payload.due_date),
        payload
    };
}

export function buildReturnPayload(formId = 'returnBookForm') {
    const formData = getFormData(formId);
    if (!formData) {
        return { isValid: false, loanId: null, payload: null };
    }

    const loanId = formData.get('loan_id');
    const returnDate = formData.get('return_date');
    const payload = {};
    if (returnDate) {
        payload.actual_return_date = returnDate;
    }

    return {
        isValid: Boolean(loanId),
        loanId,
        payload
    };
}

export function buildBookPayload(formId = 'addBookForm') {
    const formData = getFormData(formId);
    if (!formData) {
        return null;
    }

    return {
        title: formData.get('title'),
        author: formData.get('author'),
        isbn: nullableValue(formData.get('isbn')),
        publisher: nullableValue(formData.get('publisher')),
        publication_year: intValue(formData.get('publication_year')),
        pages: intValue(formData.get('pages')),
        max_loan_weeks: intValue(formData.get('max_loan_weeks'), 3),
        total_copies: intValue(formData.get('total_copies'), 1)
    };
}

export function buildMemberPayload(formId = 'addMemberForm') {
    const formData = getFormData(formId);
    if (!formData) {
        return null;
    }

    return {
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        email: nullableValue(formData.get('email')),
        address: nullableValue(formData.get('address')),
        phone: nullableValue(formData.get('phone'))
    };
}

export function buildEmployeePayload(formId = 'addEmployeeForm') {
    const formData = getFormData(formId);
    if (!formData) {
        return null;
    }

    return {
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        position: formData.get('position')
    };
}

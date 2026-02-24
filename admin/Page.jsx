import { useState, useEffect, useRef } from "react";
import { useApi, baseUrl, registerPluginTranslations } from "coffeebreak";
import { useNotification } from "coffeebreak/contexts";
import { useTranslation } from "react-i18next";
import { BiSolidBellPlus } from "react-icons/bi";
import { HiTemplate } from "react-icons/hi";
import { FaSearch, FaEdit, FaTrash, FaExclamationTriangle } from "react-icons/fa";
import en from "../locales/en.json";
import ptBR from "../locales/pt-BR.json";
import ptPT from "../locales/pt-PT.json";

const NS = "alert-system-plugin";
registerPluginTranslations(NS, { en, "pt-BR": ptBR, "pt-PT": ptPT });

const alertsBaseUrl = `${baseUrl}/alert-system-plugin`;

// --- Shared UI primitives (self-contained, no frontend imports) ---

function Modal({ isOpen, onClose, title, description, children }) {
  const ref = useRef(null);
  useEffect(() => {
    if (isOpen) ref.current?.showModal();
    else ref.current?.close();
  }, [isOpen]);
  return (
    <dialog ref={ref} className="modal rounded-md" onClose={onClose} onCancel={(e) => e.preventDefault()}>
      <div className="modal-box max-w-2xl">
        <div className="mb-6">
          <h3 className="font-bold text-lg">{title}</h3>
          {description && <p className="text-sm text-gray-500 mt-1">{description}</p>}
        </div>
        <button className="btn absolute right-2 top-2" onClick={onClose} aria-label="Close">✕</button>
        <div className="mt-4">{children}</div>
      </div>
      <button className="modal-backdrop" onClick={onClose} aria-label="Close modal" />
    </dialog>
  );
}

function FormField({ label, id, required, children }) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium mb-1">
        {label} {required && <span className="text-error">*</span>}
      </label>
      {children}
    </div>
  );
}

function DeleteModal({ isOpen, onClose, onConfirm, isLoading }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Delete Template">
      <div className="py-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="text-primary"><FaExclamationTriangle size={24} /></div>
          <p>Are you sure you want to delete this template? This action cannot be undone.</p>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button className="btn btn-ghost" onClick={onClose} disabled={isLoading}>Cancel</button>
          <button className="btn btn-primary" onClick={onConfirm} disabled={isLoading}>
            {isLoading ? <span className="loading loading-spinner loading-sm" /> : "Delete"}
          </button>
        </div>
      </div>
    </Modal>
  );
}

// --- Sub-components ---

function CreateAlertCards({ onOpenAlertModal, onOpenTemplateModal }) {
  const { t } = useTranslation(NS);
  return (
    <div className="w-full grid grid-cols-1 gap-4 mt-6 md:grid-cols-2">
      <button
        className="card bg-base-200 border-2 border-secondary hover:border-primary shadow-md hover:shadow-lg transition-all duration-300 text-left cursor-pointer"
        onClick={onOpenAlertModal}
      >
        <div className="card-body flex-row items-center gap-4">
          <BiSolidBellPlus className="text-4xl text-primary shrink-0" />
          <div>
            <h2 className="card-title">{t("createAlert.title")}</h2>
            <p className="text-sm text-gray-500">{t("createAlert.description")}</p>
          </div>
        </div>
      </button>
      <button
        className="card bg-base-200 border-2 border-secondary hover:border-primary shadow-md hover:shadow-lg transition-all duration-300 text-left cursor-pointer"
        onClick={onOpenTemplateModal}
      >
        <div className="card-body flex-row items-center gap-4">
          <HiTemplate className="text-4xl text-primary shrink-0" />
          <div>
            <h2 className="card-title">{t("createTemplate.title")}</h2>
            <p className="text-sm text-gray-500">{t("createTemplate.description")}</p>
          </div>
        </div>
      </button>
    </div>
  );
}

function AlertTemplateModal({ isOpen, onClose, onSubmit, editingTemplate, isLoading }) {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={editingTemplate ? "Edit Template" : "Create New Template"}
      description={editingTemplate ? "Update the template details below." : "Fill in the details to create a new template."}
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <FormField label="Title" id="templateTitle" required>
          <input
            type="text" id="templateTitle" name="templateTitle"
            placeholder="Enter template title"
            className="input input-bordered w-full"
            defaultValue={editingTemplate?.name || ""}
            required
          />
        </FormField>
        <FormField label="Template Message" id="templateMessage" required>
          <textarea
            id="templateMessage" name="templateMessage"
            className="textarea textarea-bordered w-full h-24"
            defaultValue={editingTemplate?.template || ""}
            placeholder="Enter template message"
            required
          />
        </FormField>
        <div className="mt-6 flex justify-end">
          <button type="submit" className="btn btn-primary" disabled={isLoading}>
            {isLoading ? <span className="loading loading-spinner loading-sm" /> : (editingTemplate ? "Update Template" : "Create Template")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function CreateAlertModal({ isOpen, onClose, onSubmit, templates: tplList, isLoading }) {
  const alertMessageRef = useRef(null);

  const handleTemplateSelect = (e) => {
    const selected = tplList.find((tpl) => String(tpl.id) === e.target.value);
    if (alertMessageRef.current) {
      alertMessageRef.current.value = selected?.template || "";
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Alert" description="Fill in the details to create a new alert.">
      <form onSubmit={onSubmit} className="space-y-4">
        <FormField label="Choose Template" id="alertTemplate">
          <select id="alertTemplate" name="selectedTemplate" className="select select-bordered w-full" defaultValue="" onChange={handleTemplateSelect}>
            <option value="">Select a template</option>
            {tplList.map((tpl) => <option key={tpl.id} value={String(tpl.id)}>{tpl.name}</option>)}
          </select>
        </FormField>
        <FormField label="Message" id="alertMessage" required>
          <textarea id="alertMessage" ref={alertMessageRef} name="alertMessage" className="textarea textarea-bordered w-full h-24" placeholder="Enter alert message" required />
        </FormField>
        <FormField label="High Priority" id="highPriority" required>
          <select id="highPriority" name="highPriority" className="select select-bordered w-full" defaultValue="" required>
            <option value="">Select</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </FormField>
        <div className="mt-6 flex justify-end">
          <button type="submit" className="btn btn-primary" disabled={isLoading}>
            {isLoading ? <span className="loading loading-spinner loading-sm" /> : "Create Alert"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function AlertFilters({ searchQuery, onSearchChange }) {
  return (
    <div className="my-4 flex items-center gap-2">
      <div className="relative flex-1 max-w-sm">
        <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          className="input input-bordered w-full pl-9"
          placeholder="Search templates..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
    </div>
  );
}

function AlertList({ templates, onEditTemplate, onDeleteTemplate }) {
  if (!templates.length) {
    return <p className="text-gray-500 my-4">No templates found.</p>;
  }
  return (
    <div className="overflow-x-auto mt-4">
      <table className="table w-full">
        <thead>
          <tr>
            <th>Name</th>
            <th>Message</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {templates.map((tpl) => (
            <tr key={tpl.id}>
              <td className="font-medium">{tpl.name}</td>
              <td className="max-w-xs truncate">{tpl.template}</td>
              <td className="flex gap-2">
                <button className="btn btn-sm btn-ghost" onClick={() => onEditTemplate(tpl)}>
                  <FaEdit />
                </button>
                <button className="btn btn-sm btn-ghost text-error" onClick={() => onDeleteTemplate(tpl.id)}>
                  <FaTrash />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// --- Main page ---

export default function Alerts() {
  const api = useApi();
  const { t } = useTranslation(NS);
  const { showNotification } = useNotification();

  const [templates, setTemplates] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [isAlertModalOpen, setIsAlertModalOpen] = useState(false);
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);

  useEffect(() => { loadTemplates(); }, []);

  const loadTemplates = async () => {
    setIsLoading(true);
    try {
      const { data } = await api.get(`${alertsBaseUrl}/template/`);
      setTemplates(data);
    } catch (error) {
      console.error("Failed to load templates:", error);
      showNotification(t("errors.loadTemplates"), "error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTemplate = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const name = formData.get("templateTitle");
    const template = formData.get("templateMessage");

    if (!name || !template) {
      showNotification(t("errors.requiredFields"), "error");
      return;
    }

    setIsLoading(true);
    try {
      if (editingTemplate) {
        const { data } = await api.put(`${alertsBaseUrl}/template/${editingTemplate.id}`, { name, template });
        setTemplates((prev) => prev.map((tpl) => (tpl.id === editingTemplate.id ? data : tpl)));
        showNotification(t("success.templateUpdated"), "success");
        setEditingTemplate(null);
      } else {
        const { data } = await api.post(`${alertsBaseUrl}/template/`, { name, template });
        setTemplates((prev) => [...prev, data]);
        showNotification(t("success.templateCreated"), "success");
      }
      setIsTemplateModalOpen(false);
    } catch (error) {
      console.error("Error with template:", error);
      showNotification(t(editingTemplate ? "alerts.errors.updateTemplate" : "alerts.errors.createTemplate"), "error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    await api.delete(`${alertsBaseUrl}/template/${templateId}`);
    setTemplates((prev) => prev.filter((tpl) => tpl.id !== templateId));
  };

  const handleCreateAlert = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const message = formData.get("alertMessage");
    const highPriority = formData.get("highPriority");

    if (!message || !highPriority) {
      showNotification(t("errors.requiredFields"), "error");
      return;
    }

    setIsLoading(true);
    try {
      await api.post(`${alertsBaseUrl}/alert/`, {
        message,
        high_priority: highPriority === "Yes",
      });
      showNotification(t("success.alertCreated"), "success");
      setIsAlertModalOpen(false);
    } catch (error) {
      console.error("Error creating alert:", error);
      showNotification(t("errors.createAlert"), "error");
    } finally {
      setIsLoading(false);
    }
  };

  const filteredTemplates = templates.filter(
    (tpl) =>
      !searchQuery ||
      tpl.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tpl.template.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  if (isLoading && templates.length === 0) {
    return (
      <div className="w-full min-h-svh p-8 flex justify-center items-center">
        <span className="loading loading-spinner loading-lg" />
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen p-4 sm:p-6 lg:p-8">
      <h1 className="text-3xl font-bold my-8">{t("title")}</h1>

      <CreateAlertCards
        onOpenAlertModal={() => setIsAlertModalOpen(true)}
        onOpenTemplateModal={() => setIsTemplateModalOpen(true)}
      />

      <h1 className="text-3xl font-bold mt-8">{t("templates.title")}</h1>

      <AlertFilters searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <AlertList
        templates={filteredTemplates}
        onEditTemplate={(tpl) => { setEditingTemplate(tpl); setIsTemplateModalOpen(true); }}
        onDeleteTemplate={handleDeleteTemplate}
      />

      <CreateAlertModal
        isOpen={isAlertModalOpen}
        onClose={() => setIsAlertModalOpen(false)}
        onSubmit={handleCreateAlert}
        templates={templates}
        isLoading={isLoading}
      />

      <AlertTemplateModal
        isOpen={isTemplateModalOpen}
        onClose={() => { setIsTemplateModalOpen(false); setEditingTemplate(null); }}
        onSubmit={handleCreateTemplate}
        editingTemplate={editingTemplate}
        isLoading={isLoading}
      />
    </div>
  );
}

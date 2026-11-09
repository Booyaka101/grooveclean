#include "Editor.h"
#include <windows.h>
#include <commctrl.h>
#include <algorithm>
#include <cmath>
#include <cstring>

namespace groove {
using namespace Steinberg;
using namespace Steinberg::Vst;
namespace {
constexpr int Width = 480, Height = 300;
constexpr int SensitivityId = 100, CleanedId = 110, OriginalId = 111, RemovedId = 112,
              BypassId = 120;
constexpr wchar_t WindowClass[] = L"GrooveCleanEditor_89BE7683";

class Editor final : public EditorView {
public:
    explicit Editor(EditController* controller) : EditorView(controller) {
        setRect(ViewRect(0, 0, Width, Height));
    }
    ~Editor() override { destroy(); }

    tresult PLUGIN_API isPlatformTypeSupported(FIDString type) override {
        return type && !std::strcmp(type, kPlatformTypeHWND) ? kResultTrue : kResultFalse;
    }
    tresult PLUGIN_API attached(void* parent, FIDString type) override {
        if (!parent || isPlatformTypeSupported(type) != kResultTrue || window_) return kResultFalse;
        HMODULE module = nullptr;
        GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
                          GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                          reinterpret_cast<LPCWSTR>(&procedure), &module);
        module_ = module;
        WNDCLASSW cls{};
        cls.lpfnWndProc = procedure;
        cls.hInstance = module;
        cls.hCursor = LoadCursor(nullptr, IDC_ARROW);
        cls.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_BTNFACE + 1);
        cls.lpszClassName = WindowClass;
        if (!RegisterClassW(&cls) && GetLastError() != ERROR_CLASS_ALREADY_EXISTS)
            return kResultFalse;
        INITCOMMONCONTROLSEX controls{sizeof(controls), ICC_BAR_CLASSES};
        if (!InitCommonControlsEx(&controls)) return kResultFalse;
        window_ = CreateWindowExW(0, WindowClass, L"GrooveClean",
            WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN, 0, 0, Width, Height,
            static_cast<HWND>(parent), nullptr, module, this);
        if (!window_) { UnregisterClassW(WindowClass, module_); return kResultFalse; }
        control(L"STATIC", L"GrooveClean", 0, 20, 16, 430, 22);
        control(L"STATIC", L"Restoration preview  |  5 seconds of buffering", 0, 20, 44, 440, 20);
        label_ = control(L"STATIC", L"Sensitivity: 0.50", 0, 20, 78, 420, 20);
        slider_ = control(TRACKBAR_CLASSW, L"", TBS_HORZ | WS_TABSTOP,
                           16, 102, 444, 32, SensitivityId);
        SendMessageW(slider_, TBM_SETRANGE, TRUE, MAKELPARAM(0, 100));
        control(L"BUTTON", L"Cleaned", BS_AUTORADIOBUTTON | WS_GROUP | WS_TABSTOP,
                20, 148, 110, 24, CleanedId);
        control(L"BUTTON", L"Original", BS_AUTORADIOBUTTON | WS_TABSTOP,
                145, 148, 110, 24, OriginalId);
        control(L"BUTTON", L"Removed", BS_AUTORADIOBUTTON | WS_TABSTOP,
                270, 148, 110, 24, RemovedId);
        control(L"BUTTON", L"Bypass (keeps audio aligned)", BS_AUTOCHECKBOX | WS_TABSTOP,
                20, 184, 420, 24, BypassId);
        status_ = control(L"STATIC", L"Warming up", 0, 20, 224, 440, 20);
        control(L"STATIC", L"Offline bounce supported. Keep host latency compensation enabled.",
                0, 20, 258, 440, 32);
        refresh();
        SetTimer(window_, 1, 100, nullptr);
        return EditorView::attached(parent, type);
    }
    tresult PLUGIN_API removed() override {
        destroy();
        return EditorView::removed();
    }

private:
    HWND control(const wchar_t* type, const wchar_t* text, DWORD style, int x, int y,
                 int width, int height, int id = 0) {
        HWND child = CreateWindowExW(0, type, text, WS_CHILD | WS_VISIBLE | style,
            x, y, width, height, window_, reinterpret_cast<HMENU>(static_cast<INT_PTR>(id)),
            reinterpret_cast<HINSTANCE>(GetWindowLongPtrW(window_, GWLP_HINSTANCE)), nullptr);
        SendMessageW(child, WM_SETFONT, reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)), TRUE);
        return child;
    }
    void edit(ParamID id, double value) {
        controller->beginEdit(id);
        controller->setParamNormalized(id, value);
        controller->performEdit(id, value);
        controller->endEdit(id);
    }
    void refresh() {
        const auto sensitivity = controller->getParamNormalized(0);
        const int percent = static_cast<int>(std::round(sensitivity * 100));
        if (GetFocus() != slider_) SendMessageW(slider_, TBM_SETPOS, TRUE, percent);
        wchar_t text[64];
        swprintf_s(text, L"Sensitivity: %.2f", sensitivity);
        SetWindowTextW(label_, text);
        const int monitor = static_cast<int>(std::round(controller->getParamNormalized(1) * 2));
        for (int i = 0; i < 3; ++i)
            SendDlgItemMessageW(window_, CleanedId + i, BM_SETCHECK,
                                monitor == i ? BST_CHECKED : BST_UNCHECKED, 0);
        SendDlgItemMessageW(window_, BypassId, BM_SETCHECK,
            controller->getParamNormalized(2) >= 0.5 ? BST_CHECKED : BST_UNCHECKED, 0);
        const wchar_t* messages[] = {
            L"Warming up: playing buffered original until ready",
            L"Ready",
            L"Overload detected: aligned original fallback was used",
            L"Unavailable: check sample rate, Python environment and worker log"
        };
        const int health = std::clamp(static_cast<int>(
            std::round(controller->getParamNormalized(3) * 3)), 0, 3);
        SetWindowTextW(status_, messages[health]);
    }
    void destroy() {
        if (window_) { KillTimer(window_, 1); DestroyWindow(window_); window_ = nullptr; }
        // Other open editors keep the class alive; the final editor unregisters it.
        // Otherwise the OS could retain a window procedure inside an unloaded DLL.
        if (module_) UnregisterClassW(WindowClass, module_);
    }
    static LRESULT CALLBACK procedure(HWND window, UINT message, WPARAM wparam, LPARAM lparam) {
        auto* self = reinterpret_cast<Editor*>(GetWindowLongPtrW(window, GWLP_USERDATA));
        if (message == WM_NCCREATE) {
            self = static_cast<Editor*>(reinterpret_cast<CREATESTRUCTW*>(lparam)->lpCreateParams);
            SetWindowLongPtrW(window, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(self));
        }
        if (self) {
            if (message == WM_HSCROLL && reinterpret_cast<HWND>(lparam) == self->slider_) {
                self->edit(0, SendMessageW(self->slider_, TBM_GETPOS, 0, 0) / 100.0);
                self->refresh();
                return 0;
            }
            if (message == WM_COMMAND && HIWORD(wparam) == BN_CLICKED) {
                const auto id = LOWORD(wparam);
                if (id >= CleanedId && id <= RemovedId) self->edit(1, (id - CleanedId) / 2.0);
                if (id == BypassId) self->edit(2,
                    SendDlgItemMessageW(window, BypassId, BM_GETCHECK, 0, 0) == BST_CHECKED ? 1 : 0);
                self->refresh();
                return 0;
            }
            if (message == WM_TIMER) { self->refresh(); return 0; }
            if (message == WM_NCDESTROY) {
                self->window_ = nullptr;
                SetWindowLongPtrW(window, GWLP_USERDATA, 0);
            }
        }
        return DefWindowProcW(window, message, wparam, lparam);
    }
    HWND window_ = nullptr, slider_ = nullptr, label_ = nullptr, status_ = nullptr;
    HMODULE module_ = nullptr;
};
}

IPlugView* createEditor(EditController* controller) { return new Editor(controller); }
} // namespace groove

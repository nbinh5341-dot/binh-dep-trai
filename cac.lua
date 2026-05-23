local VIM = game:GetService("VirtualInputManager")
local Camera = workspace.CurrentCamera
local Players = game:GetService("Players")
local LocalPlayer = Players.LocalPlayer

-- Đảm bảo PlayerGui đã tải xong trên Mobile
local PlayerGui = LocalPlayer:WaitForChild("PlayerGui")

-- TẠO MÀN ĐEN CHE GIAO DIỆN CHO MOBILE
local function createMobileBlackScreen()
    if PlayerGui:FindFirstChild("MacroOverlayMobile") then
        PlayerGui.MacroOverlayMobile:Destroy()
    end

    local screenGui = Instance.new("ScreenGui")
    screenGui.Name = "MacroOverlayMobile"
    screenGui.IgnoreGuiInset = true
    screenGui.DisplayOrder = 999999
    screenGui.ResetOnSpawn = false 

    -- Khung màn hình đen
    local blackFrame = Instance.new("Frame")
    blackFrame.Size = UDim2.new(1, 0, 1, 0)
    blackFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
    blackFrame.BorderSizePixel = 0
    blackFrame.Active = true 
    blackFrame.Parent = screenGui

    -- Dòng chữ thông báo đang chạy macro
    local statusLabel = Instance.new("TextLabel")
    statusLabel.Size = UDim2.new(1, 0, 0, 30)
    statusLabel.Position = UDim2.new(0, 0, 0, 20)
    statusLabel.BackgroundTransparency = 1
    statusLabel.TextColor3 = Color3.fromRGB(120, 120, 120)
    statusLabel.Text = "MACRO MOBILE RUNNING..."
    statusLabel.TextSize = 16
    statusLabel.Font = Enum.Font.SourceSansBold
    statusLabel.Parent = blackFrame

    -- NÚT BẤM ĐỂ ẨN/HIỆN MÀN ĐEN
    local toggleButton = Instance.new("TextButton")
    toggleButton.Size = UDim2.new(0, 80, 0, 35)
    toggleButton.Position = UDim2.new(0, 10, 0, 10) 
    toggleButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50) 
    toggleButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    toggleButton.Text = "ẨN MÀN ĐEN"
    toggleButton.TextSize = 12
    toggleButton.Font = Enum.Font.SourceSansBold
    toggleButton.Parent = screenGui 

    toggleButton.MouseButton1Click:Connect(function()
        blackFrame.Visible = not blackFrame.Visible
        if blackFrame.Visible then
            toggleButton.Text = "ẨN MÀN ĐEN"
            toggleButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
        else
            toggleButton.Text = "HIỆN MÀN ĐEN"
            toggleButton.BackgroundColor3 = Color3.fromRGB(50, 150, 50) 
        end
    end)

    screenGui.Parent = PlayerGui
end

createMobileBlackScreen()

local function clickPercent(pX, pY)
    local screenSize = Camera.ViewportSize
    local x = screenSize.X * pX
    local y = screenSize.Y * pY
    VIM:SendMouseButtonEvent(x, y, 0, true, game, 0)
    task.wait(0.05)
    VIM:SendMouseButtonEvent(x, y, 0, false, game, 0)
end

local function runBloxFruitsMacro()
    while true do
        clickPercent(0.107, 0.720)
        task.wait(0.8)

        clickPercent(0.195, 0.655)
        task.wait(1.2)

        clickPercent(0.262, 0.380)
        task.wait(0.8)

        clickPercent(0.355, 0.455)
        task.wait(0.6)

        -- BƯỚC 5: Đã chuyển hẳn lên 0.900 theo ý bạn
        clickPercent(0.900, 0.720)
        task.wait(0.8)

        clickPercent(0.107, 0.720)
        task.wait(0.8)

        clickPercent(0.107, 0.095)
        task.wait(1.2)

        clickPercent(0.500, 0.360)
        task.wait(0.8)

        clickPercent(0.370, 0.650)

        task.wait(7.0) 
    end
end

task.spawn(runBloxFruitsMacro)

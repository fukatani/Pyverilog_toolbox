module TOP(CLK, RST,IN);
  input CLK, RST,IN;
  reg [2:1] reg1;
  reg [2:1] reg2;
  reg [2:1] reg3;
  wire IN; //floating
  parameter one = 1;

  always @(posedge CLK or negedge RST) begin
    if(!RST) begin
      reg1[2] <= 1'b0;
    end else begin
      reg1[2] <= IN;
    end
  end

  always @(posedge CLK or negedge RST) begin
    if(!RST) begin
      reg2[2] <= 1'b0;
    end else begin
      reg2[2] <= IN;
    end
  end

  always @(posedge CLK or negedge RST) begin
    if(!RST) begin
      reg2[1] <= 1'b0;
    end else begin
      reg2[1] <= IN;
    end
  end

  always @(posedge CLK or negedge RST) begin
    if(!RST) begin
      reg3[one] <= 1'b0;
    end else begin
      reg3[one] <= IN;
    end
  end

endmodule



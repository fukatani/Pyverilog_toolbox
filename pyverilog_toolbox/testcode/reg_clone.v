module TOP(CLK, RST,IN);
  input CLK, RST, IN;
  reg reg1,reg2,reg3,reg4;
  //reg [1:0] reg5;
  wire in1;

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg1 <= 1'b0;
    end else begin
      reg1 <= IN;
    end
  end

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg2 <= 1'b0;
    end else begin
      reg2 <= 1'b1;
    end
  end

  assign in1 = IN;

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg3 <= 1'b0;
    end else begin
      reg3 <= in1;
    end
  end

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg4 <= 1'b1;
    end else begin
      reg4 <= !in1;
    end
  end

  //not supported
  /*
  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg5[1:0] <= 2'b10;
    end else begin
      reg5[1:0] <= {!in1,in1};
    end
  end
  */

  SUB sub(CLK,RST,in1);

endmodule

module SUB(CLK,RST,IN);
  input CLK, RST, IN;
  reg reg1;

  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      reg1 <= 1'b0;
    end else begin
      reg1 <= IN;
    end
  end

endmodule
